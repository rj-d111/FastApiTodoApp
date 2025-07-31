import pytest 

def test_equal_or_not_equal():
    assert 3 == 3, "3 should be equal to 3"
    
    
def test_is_instance():
    assert isinstance("Hello", str), "'Hello' should be an instance of str"
    assert not isinstance(123, str), "123 should not be an instance of str"
    

def test_boolean():
    validated = True
    assert validated, "validated should be True"
    assert ('hello' != "world"), "'hello' should not be a world"
    assert ('hello' is  not bool), "'hello' should not be a boolean"
    

def test_type():
    assert type("Hello") is str
    assert type(999) is int
    
  
def test_greater_and_less_than():
    assert 5 > 3, "5 should be greater than 3"
    assert 100 > 4, "100 should be less than 4"  # Added message for clarity
    assert not (10 < 5), "10 should not be less than 5"
    

def test_list():
    my_list = [1, 2, 3]
    assert len(my_list) == 3, "List should have 3 elements"
    assert 2 in my_list, "2 should be in the list"
    assert not (4 in my_list), "4 should not be in the list"
    my_false_list = [False, False]
    assert not  any(my_false_list), "List should not contain any True values"
    

class Student:
    def __init__(self, first_name: str, last_name:str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years
        
        
@pytest.fixture
def default_student():
    return Student("John", "Doe", "Computer Science", 3)
        
def test_person_initialization(default_student):
    assert default_student.first_name == "John", "First name should be John"
    assert default_student.last_name == "Doe", "Last name should be Doe"
    assert default_student.major == "Computer Science", "Major should be Computer Science"
    assert default_student.years == 3, "Years should be 3"