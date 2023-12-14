from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class ExpressionConverter:
    def __init__(self):
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        self.associativity = {'+': 'LR', '-': 'LR', '*': 'LR', '/': 'LR', '^': 'RL'}

    def is_operator(self, char):
        return char in self.precedence

    def higher_precedence(self, op1, op2):
        prec1, prec2 = self.precedence[op1], self.precedence[op2]
        if prec1 == prec2:
            if self.associativity[op1] == 'LR':
                return True
            elif self.associativity[op1] == 'RL':
                return False
        return prec1 > prec2

    def infix_to_postfix(self, infix_expression):
        postfix = []
        stack = []
        steps = []

        def visualize_step(char):
            stack_str = " ".join(stack) if stack else "Empty"
            postfix_str = " ".join(postfix) if postfix else "Empty"
            steps.append((char, stack_str, postfix_str))

        visualize_step("")  # Initial step
        for char in infix_expression:
            if char.isalnum():  # Operand
                postfix.append(char)
                visualize_step(char)
            elif char == '(':
                stack.append(char)
                visualize_step(char)
            elif char == ')':
                while stack and stack[-1] != '(':
                    postfix.append(stack.pop())
                    visualize_step(char)
                if stack:
                    stack.pop()  # Discard '(' from the stack
                    visualize_step(char)
                else:
                    steps.append(("Error: Mismatched parentheses.", "", ""))
                    return steps
            elif self.is_operator(char):
                while stack and self.is_operator(stack[-1]) and self.higher_precedence(stack[-1], char):
                    postfix.append(stack.pop())
                    visualize_step(char)
                stack.append(char)
                visualize_step(char)

        while stack:
            postfix.append(stack.pop())
            visualize_step("")

        steps.append(("Final", "", " ".join(postfix) if postfix else "Empty"))
        return steps

    def postfix_to_infix(self, postfix_expression):
        stack = []
        steps = []

        def visualize_step(char):
            stack_str = " ".join(stack) if stack else "Empty"
            steps.append((char, stack_str))

        visualize_step("")  # Initial step
        for char in postfix_expression:
            if char.isalnum():  # Operand
                stack.append(char)
                visualize_step(char)
            elif self.is_operator(char):
                if len(stack) < 2:
                    steps.append(("Error: Insufficient operands for operator.", ""))
                    return steps
                operand2 = stack.pop()
                operand1 = stack.pop()
                new_expression = f"({operand1} {char} {operand2})"
                stack.append(new_expression)
                visualize_step(char)

        if len(stack) == 1:
            steps.append(("Final", stack[0]))
            return steps
        else:
            steps.append(("Error: Invalid postfix expression.", ""))
            return steps

    def infix_to_prefix(self, infix_expression):
        prefix = []
        stack = []
        steps = []

        def visualize_step(char):
            stack_str = " ".join(stack) if stack else "Empty"
            prefix_str = " ".join(prefix[::-1]) if prefix else "Empty"
            steps.append((char, stack_str, prefix_str))

        visualize_step("")  # Initial step
        for char in infix_expression[::-1]:  # Reverse the input expression
            if char.isalnum():  # Operand
                prefix.append(char)
                visualize_step(char)
            elif char == ')':
                stack.append(char)
                visualize_step(char)
            elif char == '(':
                while stack and stack[-1] != ')':
                    prefix.append(stack.pop())
                    visualize_step(char)
                if stack:
                    stack.pop()  # Discard ')' from the stack
                    visualize_step(char)
                else:
                    steps.append(("Error: Mismatched parentheses.", "", ""))
                    return steps
            elif self.is_operator(char):
                while stack and self.is_operator(stack[-1]) and self.higher_precedence(stack[-1], char):
                    prefix.append(stack.pop())
                    visualize_step(char)
                stack.append(char)
                visualize_step(char)

        while stack:
            prefix.append(stack.pop())
            visualize_step("")

        steps.append(("Final", "", " ".join(prefix[::-1]) if prefix else "Empty"))
        return steps

    def prefix_to_infix(self, prefix_expression):
        stack = []
        steps = []

        def visualize_step(char):
            stack_str = " ".join(stack) if stack else "Empty"
            steps.append((char, stack_str))

        visualize_step("")  # Initial step
        for char in reversed(prefix_expression):  # Reverse the input expression
            if char.isalnum():  # Operand
                stack.append(char)
                visualize_step(char)
            elif self.is_operator(char):
                if len(stack) < 2:
                    steps.append(("Error: Insufficient operands for operator.", ""))
                    return steps
                operand1 = stack.pop()
                operand2 = stack.pop()
                new_expression = f"({operand1} {char} {operand2})"
                stack.append(new_expression)
                visualize_step(char)

        if len(stack) == 1:
            steps.append(("Final", stack[0]))
            return steps
        else:
            steps.append(("Error: Invalid prefix expression.", ""))
            return steps
    
expression_converter = ExpressionConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    expression = request.form['expression']
    conversion_type = request.form['conversion_type']

    steps = []

    if conversion_type == 'infix_to_postfix':
        steps = expression_converter.infix_to_postfix(expression)
    elif conversion_type == 'postfix_to_infix':
        steps = expression_converter.postfix_to_infix(expression)
    elif conversion_type == 'infix_to_prefix':
        steps = expression_converter.infix_to_prefix(expression)
    elif conversion_type == 'prefix_to_infix':
        steps = expression_converter.prefix_to_infix(expression)
    # Add other conversion types as needed

    return jsonify({'steps': steps})

if __name__ == '__main__':
    app.run(debug=True)
