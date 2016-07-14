yum install nfs-utils
systemctl enable rpcbind
systemctl enable nfs-server
systemctl enable nfs-lock
systemctl enable nfs-idmap
systemctl start rpcbind
systemctl start nfs-server
systemctl start nfs-lock
systemctl start nfs-idmap

input=$1

if [ ! -z "${input// }" -a "$1" == "server" ];
then
       mkdir /var/export
       chmod -R 777 /var/nfsshare/
       sed -i 's~/var/export.*~~g' /etc/exports
       echo "/var/export *(rw,sync,no_root_squash,no_all_squash)" >> /etc/exports
       mkdir -p /var/export/automation/Automation-distros/repo_mirror
       mkdir -p /var/export/automation/virtenv
       mkdir -p /var/export/test_result_archive
       systemctl restart nfs-server 
fi



