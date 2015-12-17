# coding=utf-8
from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData
import time
from django.template import Context, Template
from os import environ as env
import requests

wechat_template = """Service {{ service.name }}  {% if service.overall_status != service.PASSING_STATUS %}alerting with status: {{ service.overall_status }}{% else %}is back to normal{% endif %}.
{% if service.overall_status != service.PASSING_STATUS %}
CHECKS FAILING:{% for check in service.all_failing_checks %}
  FAILING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% if service.all_passing_checks %}
Passing checks:{% for check in service.all_passing_checks %}
  PASSING - {{ check.name }} - Type: {{ check.check_category }} - Importance: {{ check.get_importance_display }}{% endfor %}
{% endif %}
{% endif %}
"""


class WechatAlert(AlertPlugin):
    name = "Wechat Alert"
    author = "xiaolong.yuanxl"

    def send_alert(self, service, users, duty_officers):
        """Implement your send_alert functionality here."""

        # 获取 service 状态 如果不是 PASSING 则报警
        if service.overall_status != service.PASSING_STATUS:
            title = '%s status for service: %s' % (
                service.overall_status, service.name)
        else:
            title = 'Service back to normal: %s' % (service.name,)

        # 渲染正文
        t = Template(wechat_template)
        c = Context({
            'service': service
        })
        content = t.render(c)

        # 记日志
        print "[Wechat Alert] 时间:{0}\n标题:{1}\n内容:{2}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), title, content)

        # 发送逻辑
        requests.post('wechatmessage.echele.cn/sendMessage', data={
            "title": title,
            "content": content,
            "appType": "ALERT"
        })

        return


class WechatAlertUserData(AlertPluginUserData):
    name = "Wechat Plugin"
    favorite_bone = models.CharField(max_length=50, blank=True)
