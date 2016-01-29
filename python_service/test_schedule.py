__author__ = 'xiaohe'

from schedule_debug import schedule

if __name__ == "__main__":
    test_dict = {
        'gpa': 3.7,
        'current-school':8,
        'toefl': {
            'total': 103,
            'speaking': 25,
        },
        'ielts': {
            'total': 7,
        },
        'gre': {
            'total': 327,
            'v': 157,
        },
        'research': {
            'duration': 3,  # 0-99h
            'level': 0,  # 国家级实验室 or 国家重点项目
            'achievement': 0,  # SCI一作
            'recommendation': 1,  # 是，讲师级别的推荐信
        },
        'work': {
            'duration': 4,  # 无
            'level': 0,  # 默认
            'recommendation': 0,  # 默认
        },
        'internship': {
            'duration': 7,  # 无
            'level': 0,  # 默认
            'recommendation': 0,  # 默认
        },
        'scholarship': {
            'level': 2,  # 校级一等奖
        },
        'activity': {
            'duration': 2,
            'type': 2,  #
        },
        'credential': {
            'level': 1,  # 默认值
        },
        'competition': {
            'level':  3,  # 默认值
        },
     }
    condition = {
        u'grade': 2,
        u'target': 2,
        u'conditon': test_dict,
    }

    result = schedule(condition)

    #输出结果
