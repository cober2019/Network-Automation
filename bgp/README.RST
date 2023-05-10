***BGP PRefix Check***

The orginal use for this code was to ensure public my public prefixs wern't being advertised on the internet.

Modify the BGP check for your use case:
IDEA : I would assume you would check to see if anyone is stealing you public prefix. You could modify the code to see who's originating your prefix.

!Your prefixes will be verified on public route servers, using telnet. iF YOU COULD FIND PUBLIC ssh SERVERS, you could test those.!
