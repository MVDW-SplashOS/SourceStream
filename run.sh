#!/bin/env bash
# A tool to download, repack and push core packages for SplashOS
# Written by MVDW for SplashOS
set -e

export LANG=C
export VERSION_STR="1.2.0"
export VERSION_DATE="7 Aug 2023"

export DOWNLOAD_RETRYS=0
export DOWNLOAD_RETRYS_MAX=3

# Formatting functions
separator() {
	echo "--------------------------------------------------------------------"
}

echo_ok() {
	printf "[ \e[32mOK\e[0m ] $1\n"
}

echo_fail() {
	printf "[\e[31m\e[1mFAIL\e[0m] \e[1m%s\e[0m\n" "$*"
}

echo_warn() {
	printf "[\e[0;93mWARN\e[0m] $1\n" ""
}

echo_info() {
	printf "[INFO] $1\n"
}

# Include dependency
source ./lib/parse_yaml.sh

clone_buildscript_repo() {
	echo_info "Starting cloning buildscript repo..."
	if ! test -d ./input/buildscripts; then
		git clone https://github.com/MVDW-SplashOS/BuildScripts.git ./input/buildscripts -q
	fi
}

download_tools_list() {
	echo_info "Starting to download and check packages, this can take a while..."

	for TOOL in ${config_tools_enabled_[*]}; do
		eval "TOOL_VERSION=\${config_tools_list__${TOOL}__version}"
		eval "TOOL_URL=\${config_tools_list__${TOOL}__url/\{VERSION\}/"$TOOL_VERSION"}"
		eval "TOOL_URL=\${TOOL_URL/\{VERSION\}/"$TOOL_VERSION"}" # if there is a 2nd version string in the url(too lazy for a propper fix)
		eval "TOOL_PATCH=\${config_tools_list__${TOOL}__patch/\{VERSION\}/"$TOOL_VERSION"}"
		eval "TOOL_MD5=\${config_tools_list__${TOOL}__checksum}"

		bn=$(basename $TOOL_URL)

		if ! test -f ./input/$bn; then
			download_tool $TOOL_URL $bn
			check_tool $TOOL $TOOL_URL $bn
		else
			check_tool $TOOL $TOOL_URL $bn

		fi

	done

}

download_tool() {
	rm -rf "./input/$bn"
	wget -q $TOOL_URL -O ./input/$bn
	echo_ok "Downloaded package \e[1;37m${TOOL}\e[0m Successfully."
}

check_tool() {
	if [[ $(md5sum "./input/$bn") != $TOOL_MD5* ]]; then

		((DOWNLOAD_RETRYS = DOWNLOAD_RETRYS + 1))

		if [ $DOWNLOAD_RETRYS != $DOWNLOAD_RETRYS_MAX ]; then
			echo_warn "Checksum of package \e[1;37m${TOOL}\e[0m does not match, retrying (${DOWNLOAD_RETRYS}/${DOWNLOAD_RETRYS_MAX})"
			download_tool $TOOL $TOOL_URL $bn
		else
			echo_fail "Checksum of package ${TOOL} does not match and reached the maximum retries."
			exit
		fi
	fi

}

unpack_tool() {
	echo_info "Starting to repack packages, this can take a while..."
	cd ./input

	for TOOL in ${config_tools_enabled_[*]}; do
		eval "TOOL_VERSION=\${config_tools_list__${TOOL}__version}"
		eval "TOOL_URL=\${config_tools_list__${TOOL}__url/\{VERSION\}/"$TOOL_VERSION"}"
		eval "TOOL_URL=\${TOOL_URL/\{VERSION\}/"$TOOL_VERSION"}" # if there is a 2nd version string in the url(too lazy for a propper fix)
		eval "TOOL_PATCH=\${config_tools_list__${TOOL}__patch/\{VERSION\}/"$TOOL_VERSION"}"

		bn=$(basename $TOOL_URL)
		dir=$(echo $bn | awk -F"\\\\.t" '{print $1}')

		# Dirty fix for tcl docs package
		dir=$(echo $dir | awk -F"\\\\-src" '{print $1}')
		if [ $TOOL = "tcl_docs" ]; then
			dir=$(echo $dir | awk -F"\\\\-html" '{print $1}')
		fi

		# Dirty fix for tzdata package
		if [ $TOOL = "tzdata" ]; then
			mkdir -p ${TOOL}-${TOOL_VERSION}
			cd ${TOOL}-${TOOL_VERSION}
			echo $bn
			tar --overwrite -xf ../$bn
			cd ..
		else
			tar --overwrite -xf ./$bn

			if ! [ $dir == "${TOOL}-${TOOL_VERSION}" ]; then
				mv $dir ${TOOL}-${TOOL_VERSION}
			fi
		fi

		mkdir -p ../output/${TOOL}
		if ! test -d buildscripts/${TOOL}; then
			tar -cJf ../output/${TOOL}/${TOOL}-${TOOL_VERSION}.tar.xz ${TOOL}-${TOOL_VERSION}
			echo_warn "The package $TOOL does not have a manifest."
		else
			tar -cJf ../output/${TOOL}/${TOOL}-${TOOL_VERSION}.tar.xz -C . ${TOOL}-${TOOL_VERSION} -C buildscripts/${TOOL} . 
		fi
		rm -rf ./${TOOL}-${TOOL_VERSION}
		echo_ok "Package \e[1;37m${TOOL}\e[0m repacked successfully."
	done
}

# Program starts here
main() {

	# Print basic tool information
	separator
	printf "\n"
	printf "\e[1;36mSourceStream\n"
	printf "\e[0;36mA tool to download, patch and repack core packages for SplashOS\n"
	printf "Version: $VERSION_STR ($VERSION_DATE)\e[0m\n"
	printf "\n"
	separator

	# Create input/output directory
	mkdir -p {input,output}
	echo_info "Created input/output directory's."

	# Parse config file

	echo_info "Reading config file."
	export yaml_file=./config.yml
	export yaml_prefix="config_"
	create_variables

	if [ $config_edition = "custom" ]; then
		echo_info "Using custom edition, Checking if file is valid."
		# TODO: Do checks if file is valid.
	else
		echo_info "Get source file from $config_edition edition."
		wget -q https://www.enthix.net/SplashOS/downloads/configs/edition-packages/${config_version}/${config_edition}.yml -O ./edition-sources.yml
	fi
	export yaml_file=./edition-sources.yml
	export yaml_prefix="config_"
	create_variables

	clone_buildscript_repo
	echo_info "Cloning buildscript repository has been complete."

	download_tools_list
	echo_info "Downloading and checking packages has been complete."

	unpack_tool
	echo_info "Repacking tools has been complete."

	separator
	printf "\n"
	printf "Finished all processes."
	printf "\n"
	exit
}

main
