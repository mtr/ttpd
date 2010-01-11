# !/bin/bash
#

if [ -z "$1" ]; then
    echo "Usage: $0 <remote host>:[remote directory]"
fi

destination=$1
ssh_key=$HOME/.ec2/Main.pem

account=$(echo $destination |sed 's/\(.*\):\(.*\)/\1/g' -)
remote_dir=$(echo $destination \
    |sed 's/\(.*\):\(.*\)/\2/g' - \
    |sed 's/[/]*$//g' -) 

latest_deb=$(ls dist/*.deb |sort |tail -1)

cmd="scp -i $ssh_key $latest_deb $account:$remote_dir/"
echo $cmd
$cmd

deb=$(basename $latest_deb)

cmd="ssh -i $ssh_key $account /bin/bash -c 'sudo dpkg --install $remote_dir/$deb'"
echo $cmd
$cmd
