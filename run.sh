#/bin/bash

main() {
	clear
	rm -rf __pycache__/ vfaspi.db*
	figlet -f small "vFAPI"
	echo -e "\t\tvulnerable FastAPI"
	echo "[+] Starting Vulnerable API"
	python3 main.py
}

main
while [[ $1 == ""--reload ]]; do
	main;
done
