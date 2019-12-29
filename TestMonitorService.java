package jmx_test;

import java.lang.management.ManagementFactory;

import javax.management.InstanceAlreadyExistsException;
import javax.management.MBeanRegistrationException;
import javax.management.MBeanServer;
import javax.management.MalformedObjectNameException;
import javax.management.NotCompliantMBeanException;
import javax.management.ObjectName;
import javax.management.StandardMBean;

public class TestMonitorService {
	public static void main(String args[]) throws InstanceAlreadyExistsException, MBeanRegistrationException, NotCompliantMBeanException, MalformedObjectNameException, InterruptedException{
		System.out.println("Hello world!");
		MemoryUsageMonitorMBean monitor = new MemoryUsageMonitorMBean(); // Create MBean object
		String name = "com.cybozu.server:type=MemoryUsageMonitorMBean"; // MBean name
		StandardMBean mbean = new StandardMBean(monitor, TestMonitorMBean.class);
		
		MBeanServer mBeanServer = ManagementFactory.getPlatformMBeanServer(); // get MBeanServer 
		mBeanServer.registerMBean(mbean, new ObjectName(name)); // Register
		
		while(true){
			System.out.println("Memory count:" + monitor.getMemoryUsage());
			Thread.sleep(10000);
		}
	}
}
