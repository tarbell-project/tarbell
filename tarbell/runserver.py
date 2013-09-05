from tarbell.app import TarbellSite
import sys

if __name__ == '__main__':
    # @TODO get arg
    print "\nRunning server, press ctrl c to stop!!\n"
    print sys.argv[1]
    site = TarbellSite(sys.argv[1])
    address_parts = sys.argv[2].split(':')
    ip = address_parts[0]
    port = '5000'
    if len(address_parts) > 1:
        port = address_parts[1]
    print "ip: %s" % ip
    print "port: %s" % port
    site.app.run(ip, port=int(port))
