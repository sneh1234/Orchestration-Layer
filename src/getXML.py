import uuid
def get(name , id, nocpu, ram, disk,image):
   
    print image.split()[0]
    print image
    xml="""<domain type='kvm' id='{0}'>
      <name>{1}</name>
      <uuid>{2}</uuid>
      <memory unit='KiB'>{3}</memory>
      <currentMemory unit='KiB'>{3}</currentMemory>
      <vcpu placement='static'>{4}</vcpu>
      <resource>
        <partition>/machine</partition>
      </resource>
      <os>
        <type arch='x86_64' machine='pc-i440fx-trusty'>hvm</type>
        <boot dev='hd'/>
      </os>
      <features>
        <acpi/>
        <apic/>
        <pae/>
      </features>
      <clock offset='utc'/>
      <on_poweroff>destroy</on_poweroff>
      <on_reboot>restart</on_reboot>
      <on_crash>restart</on_crash>
      
      <devices>
  <disk type='file' device='disk'>
  <source file='{5}'/>
  <target dev='hda' bus='ide'/>
  </disk>
  </devices>
      
    </domain>""".format(id,name,uuid.uuid4(), ram, nocpu,image)
    return xml

