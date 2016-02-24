import json
import assess_student
from assess_student import assess_student

student_info = {
    "major":"tesol",
    "grade":"1",
    "target":"1",
    "data":{
        "gpa":{"score":"3.2", "trend":"2", "school":"华中科技大学|湖北|985"},
        "gmat":{"total":"300", "writing":"3", "verbal":"12", "maths":"12"},
        "gre":{"total":"300", "writing":"4", "verbal":"12", "maths":"12"},
        "toefl":{"total":"110", "writing":"3", "reading":"12", "listening":"12", "speaking":"12"},
        "ielts":{"total":"7", "writing":"3", "reading":"12","listening":"12", "speaking":"12"},
        "research":{"duration":"1", "level":"1", "achievement":"1", "recommendation":"1"},
        "work":{"duration":"1", "level":"1", "recommendation":"1"},
        "internship":{"duration":"1", "level":"1", "recommendation":"1"},
        "reletter":{"level":["1","2","3"]},
        "activity":{"duration":"1", "type":"1"},
        "credential":{"level":"2"},
        "competition":{"level":"2"},
        "scholarship":{"level":"2"}
    }
}

print(json.dumps(assess_student(student_info), ensure_ascii=False, indent=4))