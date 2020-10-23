# Bit Torrent - Peer to Peer file system
## Project Objectives
* In this project, I implemented a simple peer-to-peer (P2P) system with a distributed index (DI).
* This project helped me understand and learn the following:
  *  becoming familiar with network programming and the socket interface,
  * creating server processes that wait for connections,
  * creating client processes that contact a well-known server and exchange data over the Internet,
  * defining a simple application protocol and making sure that peers and server follow precisely the specifications for their side of the protocol in order to accomplish particular tasks,
  * creating and managing a distributed index among multiple peers, and
  * implementing a concurrent server that is capable of carrying out communication with multiple clients simultaneously.

## Design and Implementation:
### Peer-to-Peer with Distributed Index (P2P-DI) System for Downloading RFCs
* Internet protocol standards are defined in documents called “Requests for Comments” (RFCs). RFCs are available for download from the IETF web site (http://www.ietf.org/).
* Rather than using this **centralized server** for downloading RFCs, I built a ***P2P-DI system*** in which peers who wish to download an RFC that they do not have in their hard drive, may download it from another active peer who does. 
* All communication among peers or between a peer and the registration server will take place over TCP.

### Specifically, the P2P-DI system will operate as follows; 
* A registration server (RS), running on a well-known host and listening on a well-known port, keeps information about the active peers. The RS does not keep any information about the RFCs that the various active peers may have.
* When a peer decides to join the P2P-DI system, it opens a connection to the RS to register itself. If this is the first time the peer registers with the P2P-DI system, it is given a ***cookie*** by the RS which identifies the peer. The cookie is used by the peer in all subsequent communication with the RS. In this project, the cookie can be a small integer, unique to each peer.
* The peer closes this connection after registration. When a peer decides to leave the P2P-DI system, it opens a new connection to the RS to inform it, and the RS marks the peer as inactive.
* Note, Inorder to simulate a real world example of a peer-to-peer system, I have designed it so that a peer may leave the system without issuing a leave request, e.g., because the peer host crashed or the user turned off the system.
* Each peer maintains an RFC index with information about RFCs it has locally, as well as RFCs maintained by other peers it has recently contacted. It also runs an RFC server that other peers may contact to download RFCs.
* Finally, it also runs an RFC client that it uses to connect to the RS and the RFC server of remote peers.

### Corner cases and error handling:
* When a peer **PA** wishes to download a specific RFC that it does not have locally, it opens a new connection to the RS and requests a list of active peers. In response, the RS provides **PA** with a list of all peers who are currently active; if no such active peer exists, an appropriate message is transmitted to the requesting peer. 
* Peer **PA** then opens a connection to one of the other active peers, say, **PB**, and requests its RFC index. When PA receives the RFC index from PB, it (1) merges it with its own RFC index, and (2) searches its new RFC index (after the merge) to find any active peer that has the RFC it is looking for. If the RFC index indicates that some active peer PC has the RFC, **PA** opens a new connection to the RFC server of PC to download the RFC (note, however that **PC** may have left the system by this time, and this connection may be unsuccessful). 
* If **PA** does not find any peer that has the RFC, or if its connection to PC is unsuccessful, then it contacts another peer, say, **PD**, in the list of active peers it received from the RS. This process continues until either **PA** successfully downloads the RFC or the list of active peers is exhausted.
* The RFC server at a peer listens on a port specific to the peer ; in other words, this port is not known in advance to any of the peers. 

### Multi-threaded client system
* The RFC server at each peer is able to handle multiple simultaneous connections for downloads (of the RFC index or an RFC document) by remote peers. To this end, it has a main thread that listens to the peer-specific port. When a connection from a remote peer is received, the main thread spawns a new thread that handles the downloading for this remote peer.
* The main thread then returns to listening for other connection requests. Once the downloading is complete, this new thread terminates.

### The Registration Server (RS)
* The RS waits for connections from the peers on the well-known port 654231. The RS maintains a peer list data structure with information about the peers that have registered with the RS at least once. 
* For simplicity, I implemented this data structure as a list; while such an implementation is obviously not scalable to very large numbers of peers, it will do for this project.
* Each record of the peer list contains seven elements:
  1. the hostname of the peer (of type string),
  2. the cookie (of type integer) assigned to the peer (if the peer is on the list, it must have registered, therefore it has a cookie),
  3. a flag (of type Boolean) that indicates whether the peer is currently active,
  4. a TTL field (of type integer); it is initialized to a value of 7200 (in seconds) every time a peer contacts the RS (to register or ask for the peer list), and is decremented periodically so that whenever it reaches 0 the peer is flagged as inactive,
  5. the port number (of type integer) to which the RFC server of this peer is listening; note that this field is valid only if the peer is active,
  6. the number of times (of type integer) this peer has been active (i.e., has registered) during the last 30 days, and
  7. the most recent time/date that the peer registered. 

## The Peers
* Each peer maintains a local RFC index, that initially contains information only on RFCs stored locally at the peer. When the peer retrieves the RFC index of a remote peer, it merges it with its local copy, i.e., it updates its RFC index to include information about RFCs maintained by the remote peer. 
* Upon a request from a remote peer, this peer provides a copy of the whole RFC index it maintains (i.e., including local and remote RFCs it knows about).

### Each record of the RFC index contains four elements:
  * the RFC number (of type integer),
  * the title of the RFC (of type string),
  * the hostname of the peer containing the RFC (of type string), and
  * a TTL field (of type integer). For RFCs maintained locally, this value is set to 7200 (in seconds) and never modified. For RFCs maintained at a remote peer, the TTL value is initialized to 7200 at the time the RFC index from this remote peer is received, and is decremented periodically thereafter.
*Note that the index may contain multiple records of a given RFC, one record for each peer that has a copy of the RFC document.*

## The Application Layer Protocol: P2P
The protocol for peers to communicate with the RS and among themselves. In particular, the protocol runs over TCP and supports the following types of messages:
### For peer-to-RS communication:
  1. ***Register***: the peer opens a TCP connection to send this registration message to the RS and provide information about the port to which its RFC server listens.
  2. ***Leave***: when the peer decides to leave the system (i.e., become inactive), it opens a TCP connection to send this message to the RS.
  3. ***PQuery***: when a peer wishes to download a query, it first sends this query message to the RS (by opening a new TCP connection), and in response it receives a list of active peers that includes the hostname and RFC server port information.
  4. ***KeepAlive***: a peer periodically sends this message to the RS to let it know that it continues to be active; upon receipt of this message, the RS resets the TTL value for this peer to 7200.

### For peer-to-peer communication:
1. ***RFCQuery***: a peer requests the RFC index from a remote peer.
2. ***GetRFC***: a peer requests to download a specific RFC document from a remote peer.
  * This protocol may be defined as a simplified version of the HTTP protocol. Suppose that peer ***A*** wishes to communicate with peer ***B*** running at host somehost.csc.ncsu.edu. Then, ***A*** may send to ***B*** a request message formatted as follows, where ```<sp>``` denotes “space,” ```<cr>``` denotes “carriage return,” and ```<lf>``` denotes “line feed.”
  ```
  method <sp> document <sp> version <cr> <lf>
  header field name <sp> value <cr> <lf>
  header field name <sp> value <cr> <lf>
  <cr> <lf>
  ```

### More about RFCQuery
* In this case, there is only one method defined, ***GET***, that can be used to implement both the ***RFCQuery*** and ***GetRFC*** message above. You may also define certain header fields, e.g., Host (the hostname of the peer from which the RFC is requested) and OS (the operating system of the requesting host). In this case, 
* the ***RFCQuery*** request message would look like this:
```
GET RFC-Index P2P-DI/1.0
Host: somehost.csc.ncsu.edu
OS: Mac OS 10.4.1
```
* the ***GetRFC*** request message would look like this:
```
GET RFC 1234 P2P-DI/1.0
Host: somehost.csc.ncsu.edu
OS: Mac OS 10.4.1
```
* The response message may also be formatted similarly:
```
version <sp> status code <sp> phrase <cr> <lf>
header field name <sp> value <cr> <lf>
header field name <sp> value <cr> <lf>
...
<cr> <lf>
data
```
* where the *data* field contains the RFC index or RFC document text file, depending on the request message.

## Typical Sequence of Messages
![alt text](https://github.com/ssudher/BitTorrent_/blob/master/client_serverComm.PNG)
* Figure 1 depicts the steps required for Peer A to register with the RS and download an RFC from Peer B. Before it joins the system, A first instantiates an RFC server listening to a local port in the range 65400-65500.
  1) In Step 1, Peer A registers with the RS, provides the local port number for its RFC server, and receives a cookie (if this is not the first time that Peer A registers with the RS, then it provides the cookie it received earlier in its Register message). 
  2) The RS updates A’s record to active and initializes the corresponding TTL value; if this was the first time A registered, then the RS creates a new peer record for A and adds it to its peer index. 
  3) In Step 3, Peer A issues a PQuery message to the RS, and in response it receives a list of active peers. Recall that the list of peers returned by the RS includes the port number used by each peer’s RFC server. Let us assume that Peer B is in this active list, and that B has the RFC
that A is looking for. 
  4) In Step 4, A issues an RFCQuery message to B, and in response it receives the RFC index that B maintains. A merges B’s RFC Index with its own index. Since we have assumed that B has the desired RFC, A then issues a GetRFC message to B and downloads the RFC text document.
  5) Finally, in Step 5, Peer A sends a Leave message to the RS and leaves the system; the RS updates A’s record to inactive.

*Note that a peer sends each message (request, query, keep alive, etc.) to the RS by opening a new TCP connection; it receives corresponding responses over the same TCP connection. The TPC connection is closed at the end of each message exchange. Similarly, a peer opens separate TPC connections to a remote peer to request the RFC index and to download an RFC.*
