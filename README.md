Installing:

git clone https://github.com/jmalsbury/gr-mac
cd gr-mac
mkdir build
cd build
cmake ../
make 
sudo make install


To run the radios:

1) Open both gmsk_radio.grc and ofdm_radio.grc.  Generate both.  This will produce the required hier blocks in ~/.grc_gnuradio

2) Close GRC or hit the "reload" block button.

3) Open simple_trx.grc and generate.

4) Run simply_trx.py with something like:


python simple_trx.py --port 12345

