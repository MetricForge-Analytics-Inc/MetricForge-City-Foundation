#!/bin/bash
set -o errexit   # abort on nonzero exitstatus
set -o nounset   # abort on unbound variable
set -o pipefail  # don't hide errors within pipes

cd Foundry-Visualization/
npm run sources
npm run dev -- --host 0.0.0.0 --port 3000