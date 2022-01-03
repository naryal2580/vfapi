#/bin/bash

# TODO: Custom Ports

export host="127.0.0.1"
export ui_port=8008
export api_port=8888
export script_dir=$PWD

banner () {
	figlet -f small "vFAPI"
}

check_ports() {
	ui_check=$(nc -zw5 $host $ui_port)
	if [[ $? -eq 0 ]]; then
		echo "[-] Looks like port ://$host:$ui_port/ is already occupied. Please kill/stop the running service conflicting the port number."
		if [[ $1 != "--ignore" ]]; then
			exit 1;
		fi
	fi
	api_check=$(nc -zw5 $host $api_port)
	if [ $? -eq 0 ]; then
		echo "[-] Looks like a service is already running on ://$host:$api_port/"
		if [[ $1 != "--ignore" ]]; then
			exit 1;
		fi
	fi
}

main() {
	# clear
	rm -rf __pycache__/ vfaspi.db*
	banner
	echo -e "\t\tvulnerable FastAPI\n"
	if [[ $1 == "--reload" ]]; then
		check_ports --ignore
		echo "[+] Starting Vulnerable API UI <dev>"
		cd ui && npm run dev -- --port 8008 &
	else
		check_ports
		echo "[+] Starting Vulnerable API UI"
		cd ui && npm run build && clear; banner; npm run preview -- --host --port 8008 &
	fi
	sleep 0.48
	echo "[+] Starting Vulnerable API <dev>"
	cd $script_dir && python3 main.py --host 
}

while [[ $1 == "--reload" ]]; do
	main --reload;
done

if [[ $? == "0" ]]; then
	main
fi
