#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Simple Trx Mac
# Generated: Fri Sep 12 23:38:50 2014
##################################################

execfile("/home/john/.grc_gnuradio/gmsk_radio.py")
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import mac
import pmt
import time
import sys

INIT = 0
MASTER_SET = 1
MASTER_HOLD = 2
SEARCH = 3
NOMINAL = 4

from simple_trx_mac import *


if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    parser.add_option("-A", "--rx-antenna", dest="rx_antenna", type="string", default="TX/RX",
        help="Set RX antenna [default=%default]")
    parser.add_option("", "--rx-gain", dest="rx_gain", type="eng_float", default=eng_notation.num_to_str(65-20),
        help="Set RX gain [default=%default]")
    parser.add_option("", "--tx-gain", dest="tx_gain", type="eng_float", default=eng_notation.num_to_str(45),
        help="Set TX gain [default=%default]")
    parser.add_option("-t", "--arq-timeout", dest="arq_timeout", type="eng_float", default=eng_notation.num_to_str(.1*0 + 0.04),
        help="Set ARQ timeout [default=%default]")
    parser.add_option("-d", "--dest-addr", dest="dest_addr", type="intx", default=-1,
        help="Set Destination address [default=%default]")
    parser.add_option("", "--max-arq-attempts", dest="max_arq_attempts", type="intx", default=5 * 2,
        help="Set Max ARQ attempts [default=%default]")
    parser.add_option("", "--ampl", dest="ampl", type="eng_float", default=eng_notation.num_to_str(0.7),
        help="Set TX BB amp [default=%default]")
    parser.add_option("", "--port", dest="port", type="string", default="12345",
        help="Set TCP port [default=%default]")
    parser.add_option("", "--mtu", dest="mtu", type="intx", default=255,
        help="Set TCP Socket MTU [default=%default]")
    parser.add_option("", "--rx-lo-offset", dest="rx_lo_offset", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set RX LO offset [default=%default]")
    parser.add_option("", "--lo-offset", dest="lo_offset", type="eng_float", default=eng_notation.num_to_str(5e6),
        help="Set lo_offset [default=%default]")
    parser.add_option("-l", "--radio-addr", dest="radio_addr", type="intx", default=0,
        help="Set Local address [default=%default]")
    parser.add_option("-a", "--args", dest="args", type="string", default='',
        help="Set USRP device args [default=%default]")
    parser.add_option("", "--tx-lo-offset", dest="tx_lo_offset", type="eng_float", default=eng_notation.num_to_str(0),
        help="Set TX LO offset [default=%default]")
    parser.add_option("", "--rx-freq", dest="rx_freq", type="eng_float", default=eng_notation.num_to_str(915e6),
        help="Set RX freq [default=%default]")
    parser.add_option("", "--tx-freq", dest="tx_freq", type="eng_float", default=eng_notation.num_to_str(915e6),
        help="Set TX freq [default=%default]")
    parser.add_option("-r", "--rate", dest="rate", type="eng_float", default=eng_notation.num_to_str(1e6),
        help="Set Sample rate [default=%default]")
    parser.add_option("", "--samps-per-sym", dest="samps_per_sym", type="intx", default=4,
        help="Set Samples/symbol [default=%default]")
    parser.add_option("-m", "--mode", dest="mode", type="string", default="slave",
       help="Set master or slave")
    parser.add_option("-c", "--channel-index", dest="channel_index", type="int", default=0,
        help="Channel index specified for master. Not applied if slave.")
    (options, args) = parser.parse_args()
    
    antenna = "TX/RX"
    channels = [x * 1e6 for x in range(905, 915, 1)]
    period = 0.5
    state = INIT
    index = 0
    beacon_interval = 1
    
    
    #make the flowgraph
    tb = simple_trx_mac(rx_antenna=antenna, rx_gain=options.rx_gain, tx_gain=options.tx_gain, arq_timeout=options.arq_timeout, dest_addr=options.dest_addr, max_arq_attempts=options.max_arq_attempts, ampl=options.ampl, port=options.port, mtu=options.mtu, rx_lo_offset=options.rx_lo_offset, lo_offset=options.lo_offset, radio_addr=options.radio_addr, args=options.args, tx_lo_offset=options.tx_lo_offset, rx_freq=options.rx_freq, tx_freq=options.tx_freq, rate=options.rate, samps_per_sym=options.samps_per_sym, broadcast_interval=beacon_interval)
    tb.start()
    
    
    while(1):
        if state == INIT:
            #start the FG - disable transmission until next state
            tb.set_ampl(0.0)
            if options.mode == "slave":
                print "I'm a slave, searching for channel."
                index = 0
                last_byte_count = 0
                period = 0.250
                tb.set_beacon_interval = 10.0
                state = SEARCH
            elif options.mode == "master":
                tb.set_beacon_interval = 0.1
                print "I'm a master, setting channel"
                state = MASTER_SET
            else:
                print "Invalid mode '%s' specified.  Exiting." % options.mode
                sys.exit()
            
        elif state == MASTER_SET:
            
            try:
                freq = channels[options.channel_index]
                print "Setting Master to %f MHz and holding." % (freq/1e6)
                print "Turning on transmitter."
                tb.set_rx_freq(freq)
                tb.set_tx_freq(freq)
                tb.set_ampl(options.ampl)
                state = MASTER_HOLD 
                period = 15.0
            except:
                print "Could not set SDR center frequency. Most likely a bad frequency index."
                sys.exit()
        
        elif state == MASTER_HOLD:
            print "I'm in charge - RECOGNIZE!"
        
        elif state == SEARCH:
            if not tb.simple_mac.get_rx_byte_count() > last_byte_count:
                
                try:
                    freq = channels[index]
                    print "Searching.  Setting Slave to %f MHz." % (freq/1e6)
                    tb.set_rx_freq(freq)
                    tb.set_tx_freq(freq)
                    index = ( index + 1 ) % len(channels)
                except:
                    print "Could not set SDR center frequency. Most likely a bad frequency index."
                    sys.exit()
        
            else:
                print "Found downlink, moving to nominal comms state."
                state = NOMINAL
                tb.set_ampl(options.ampl)
                tb.set_tx_gain(options.tx_gain)
                period = 15.0
                
        
        elif state == NOMINAL:
            if last_byte_count == tb.simple_mac.get_rx_byte_count():
                print "No bytes received.  Return to init state"
                state = INIT
                period = 0.250
            else:
                print "Channel still active.  %d bytes received." % (tb.simple_mac.get_rx_byte_count() - last_byte_count)
            
        last_byte_count = tb.simple_mac.get_rx_byte_count()
        time.sleep(period)
