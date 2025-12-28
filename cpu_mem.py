#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rospy
import psutil
from std_msgs.msg import Float32, Float32MultiArray

def system_monitor():
    rospy.init_node('system_monitor_psutil', anonymous=True)
    
    # --- 定义发布器 ---
    pub_cpu_total = rospy.Publisher('/system/cpu/total', Float32, queue_size=10)
    pub_cpu_cores = rospy.Publisher('/system/cpu/per_core', Float32MultiArray, queue_size=10)
    pub_ram_percent = rospy.Publisher('/system/ram/percent', Float32, queue_size=10)
    pub_ram_mb = rospy.Publisher('/system/ram/used_mb', Float32, queue_size=10)

    # 设置频率 1Hz
    rate = rospy.Rate(1) 
    
    rospy.loginfo("开始监控系统资源 (使用 psutil)...")

    # psutil 在第一次调用 cpu_percent 时通常返回 0，
    # 所以我们先做一次“空读取”来初始化计数器
    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None, percpu=True)

    while not rospy.is_shutdown():
        try:
            # -------------------------------------------------
            # 1. 获取 CPU 数据
            # -------------------------------------------------
            
            # interval=None 表示非阻塞模式，利用 rospy.Rate(1) 的间隔来计算差值
            # 这样不会卡住 ROS 的循环
            
            # 总 CPU 使用率
            total_usage = psutil.cpu_percent(interval=None)
            pub_cpu_total.publish(float(total_usage))

            # 每个核心的使用率 (返回一个列表，如 [10.5, 20.1, ...])
            per_core_usage = psutil.cpu_percent(interval=None, percpu=True)
            
            # 发布数组
            cpu_msg = Float32MultiArray()
            cpu_msg.data = per_core_usage
            pub_cpu_cores.publish(cpu_msg)

            # -------------------------------------------------
            # 2. 获取 内存 数据
            # -------------------------------------------------
            
            # 获取内存详情
            mem = psutil.virtual_memory()
            
            # mem.used 是字节(bytes)，转换为 MB
            used_mb = mem.used / 1024.0 / 1024.0
            
            # 内存百分比
            ram_pct = mem.percent

            pub_ram_mb.publish(float(used_mb))
            pub_ram_percent.publish(float(ram_pct))

            rate.sleep()

        except Exception as e:
            rospy.logerr(f"监控出错: {e}")

if __name__ == '__main__':
    try:
        system_monitor()
    except rospy.ROSInterruptException:
        pass
