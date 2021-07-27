#!/bin/bash

curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-schema/release/1.3.0/DCC.combined-schema.json -o dataset/schema-combined.json
curl https://verifier-api.coronacheck.nl/v4/verifier/public_keys -o dataset/public_keys.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/country-2-codes.json -o dataset/co.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/disease-agent-targeted.json -o dataset/tg.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/test-manf.json -o dataset/ma.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/test-manf.json -o dataset/tr.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/test-type.json -o dataset/tt.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/vaccine-mah-manf.json -o dataset/ma.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/vaccine-medicinal-product.json -o dataset/mp.json
curl https://raw.githubusercontent.com/ehn-dcc-development/ehn-dcc-valuesets/release/2.0.0/vaccine-prophylaxis.json -o dataset/vp.json
