A Virtualization Orchestration Layer made in Python.


It works as  a fabric that can coordinate the provisioning of 
compute resources by negotiating with a set of Hypervisors running across 
physical servers in the datacenter. It works with rest api. It uses hello_flask for frontend. While uses Qemu, KVM, libvirt for backend.

1)image_file will contain list of path of images in local machine separated by line.

2)flavor_file.json will contain json object representing type of VM.

3)pm_file will conatin list of ip's of virtual machine.

How to Use - 
Run python hypervisor.py
then  Navigate to :
		1) http://server/vm/create?name=test_vm&instance_type=type&image_id=id. It wil create virtual machine with given parameter.
		2) http://server/vm/query?vmid=vmid . It will give info about virtual machine of id equals to  vmid.
		3) http://server/vm/destroy?vmid=vmid. It will destroy the virtual machine of id equals to vmid.
		4) http://server/vm/types. It will return the types that can be used while creating virtual machine.
		5) http://server/pm/list. It gives the list of all pc.
		6) http://server/pm/listvms?pmid=id. It lists the virtual machine that are running in pc whose pmid is id.
		7) http://server/pm/query?pmid?=id. It gives various details about that pc. For example number of virtual machine , free storage,etc.
		8) http://server/image/list . It gives list of available images. 	
		Note:If image file is not present in a particular pc. Then firstly image file is copied. Else this step is skipped.
 



Technology Used:
Qemu,Kvm, mysql, python, flask , libvirt
