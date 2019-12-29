package jmx_test;

/*
 * Testing interface for MBean
 */
public interface TestMonitorMBean {
	long getMemoryUsage();
	long getTest();
}
