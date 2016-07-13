sed -i 's/nfs-server.*//g' /etc/fstab
echo "nfs-server:/export/automation/Automation-distros /media nfs defaults 0 0" >> /etc/fstab
echo "nfs-server:/export/automation/Automation-distros/repo_mirror /var/www/cobbler/repo_mirror nfs defaults 0 0" >> /etc/fstab 
echo "nfs-server:/export/automation/virtenv /automation/virtenv nfs defaults 0 0" >> /etc/fstab
echo "nfs-seerver:/export/test_result_archive /mnt/test_result_archive nfs defaults 0 0" >> /etc/fstab

mount -a
