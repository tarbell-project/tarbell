from tarbell.app import TarbellSite
import sys

if __name__ == '__main__':
    # @TODO get arg
    print "Running server, press ctrl c to stop"
    print sys.argv
    site = TarbellSite(sys.argv[0])
    address_parts = sys.argv[1].split(':')
    ip = address_parts[0]
    port = '5000'
    if len(address_parts) > 1:
        port = address_parts[1]
    site.app.run(ip, port=port)
