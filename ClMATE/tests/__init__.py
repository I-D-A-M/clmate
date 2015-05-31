'''
Testing for ClMATE is powered by pyTest. This allows for simple testing to be carried out
in an automated way. The following is an example of a source file and test file.
>> Tests are run using 'pytest' [This is MY zsh alias!]
>> When a test fails, stdout is captured to allow for easier debugging.

http://pytest.org/latest/assert.html#assert

# SOURCE SCRIPT
```````````````
`def fib(n):
`    if n < 1:
`        print("This function is only defined for positive integers!")
`    elif int(n) != n:
`        print("This function is only defined for positive integers!")
`    elif n == 1:
`        return 1
`    elif n == 2:
`        return 2
`    else:
`        return fib(n - 2) + fib(n - 1)
```````````````````````````````````````

# TEST SCRIPT
`````````````
`from my_file import multiply, fib
`
`class Testing():
`    def test_fib(self):                <-- This test will pass.
`        assert fib(4) == 5
`
`   def test_fib_fail(self):            <-- This test will fail!
`       assert fib(-1) == 1
``````````````````````````````````
'''
