#/bin/bash

banner () {
	figlet -f small "vFAPI"
}

main() {
	# clear
	rm -rf __pycache__/ vfaspi.db*
	banner
	echo -e "\t\tvulnerable FastAPI\n"
	echo "[+] Starting Vulnerable API UI <dev>"
	cd ui && npm run build && clear; banner; npm run preview -- --host --port 8008 &
	sleep 0.48
	echo "[+] Starting Vulnerable API <dev>"
	cd .. && python3 main.py --host 
}

main
while [[ $1 == ""--reload ]]; do
	main;
done
