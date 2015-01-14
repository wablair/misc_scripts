#!/bin/sh
openssl req -new -x509 -nodes -out server.crt -keyout server.key
chmod 600 server.key

# For nginx conf:
#server {
#	listen			443;
#	ssl			on;
#	ssl_certificate         server.crt;
#	ssl_certificate_key	server.key;
#	ssl_protocols		TLSv1 TLSv1.1 TLSv1.2;
#	charset                 utf-8;
#	client_max_body_size	75M;
#
#	ssl_prefer_server_ciphers	on;
#	ssl_ciphers "EECDH+ECDSA+AESGCM EECDH+aRSA+AESGCM EECDH+ECDSA+SHA384 \
#	  EECDH+ECDSA+SHA256 EECDH+aRSA+SHA384 EECDH+aRSA+SHA256 \
#	  EECDH+aRSA+RC4 EECDH EDH+aRSA !RC4 !aNULL !eNULL !LOW !3DES !MD5 \
#	  !EXP !PSK !SRP !DSS";
#}
