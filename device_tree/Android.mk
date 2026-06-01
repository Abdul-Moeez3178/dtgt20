#
# Android.mk - Build Rules for Infinix X6871 Recovery Tree
# By Mehraan
#

LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),X6871)
include $(call all-subdir-makefiles,$(LOCAL_PATH))
endif
