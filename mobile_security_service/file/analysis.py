def analyze_app(file_instance):
    try:    
        data = file_instance.read()
        return f"{len(data)}"
    except:
        return "Произошла ошибка"
