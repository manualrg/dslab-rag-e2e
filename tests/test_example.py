from src import example

def test_hello_world():
    res = example.hello_world()
    exp = "Hello World" 
    
    assert res == exp