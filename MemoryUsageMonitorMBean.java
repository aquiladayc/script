package jmx_test;

public class MemoryUsageMonitorMBean implements TestMonitorMBean {

	private long counter = 0;
	
	@Override
	public long getMemoryUsage() {
		counter++;
		return counter;
	}

	@Override
	public long getTest() {
		return 0;
	}
	
	
}
