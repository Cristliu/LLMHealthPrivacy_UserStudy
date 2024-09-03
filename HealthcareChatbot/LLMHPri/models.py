from django.db import models

class UserSession(models.Model):
    ip_address = models.CharField(max_length=15)
    # device_info = models.CharField(max_length=255)
    # device_fingerprint = models.CharField(max_length=255, null=True, blank=True)  # 添加设备指纹字段
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)  # 存储会话持续时间
    # agree_to_participate = models.BooleanField(default=False)
    # provided_info = models.BooleanField(default=False)  # 用户是否提供了年龄、性别等信息
    # age_group = models.CharField(max_length=50, null=True, blank=True)
    # gender = models.CharField(max_length=10, null=True, blank=True)
    # occupation = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.id)  # 使用自增长的id作为唯一标识码



class Dialogue(models.Model):
    session = models.ForeignKey(UserSession, related_name='dialogues', on_delete=models.CASCADE)
    sender = models.CharField(max_length=10, choices=(('user', '用户'), ('gpt', 'GPT')))
    message = models.TextField()
    # timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}..."  # 显示发送者和消息的前50个字符