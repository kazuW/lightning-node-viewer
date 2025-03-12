def generate_line_chart(data, title, x_label, y_label):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    plt.plot(data['date'], data['value'], marker='o')
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.show()

def generate_bar_chart(data, title, x_label, y_label):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    plt.bar(data['date'], data['value'])
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid()
    plt.show()

def generate_pie_chart(data, title):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 8))
    plt.pie(data['value'], labels=data['category'], autopct='%1.1f%%')
    plt.title(title)
    plt.axis('equal')
    plt.show()