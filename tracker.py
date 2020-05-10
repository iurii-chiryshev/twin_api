from interpreter import TwinInterpreter
import random
import logging

logging.basicConfig(format="%(levelname)s %(asctime)s - %(message)s")

class ActionHandler:
    def __init__(self, confidence: float = 0.5):
        self.last_intent = None # последний обработанный интент
        self.last_entities = None # последние обработанные сущности
        self.confidence = confidence # порог принятия решения

    def process(self,intent, entities):
        """
        Основной метод, который обрабатывает входные намерения
        :param intent:
        :param entities:
        :return:
        """
        # вытаскиваем имя намерения и confidence
        name = intent.get("name","default")
        confidence = intent.get("confidence",0)
        if confidence > self.confidence:
            # если бот уверен в намеренье
            # нахомим метод обработчик, если не найдем - будет вызвана method_not_implemented
            handler = getattr(self, "on_{name}".format(name=name).lower(), self.method_not_implemented)
        else:
            # бот не уверен в намеренье
            handler = self.on_default
        # вызываем метод
        result = handler(intent, entities)
        # cохраняем намерение и сущности
        self.last_intent = intent
        self.last_entities = entities
        # вернуть результат
        return result

    def method_not_implemented(self,intent, entities):
        """
        Как обрабатвется намерение, если для него нет метода обработчика
        :param intent:
        :param entities:
        :return:
        """
        name =  intent.get("name", "")
        confidence = intent.get("confidence", 0)
        msg = "Method on_{intent_name} not implemented".format(intent_name = name)
        logging.warning(msg)
        return "Intent: {name}, confidence: {confidence}".format(name = name, confidence = confidence)

    def on_default(self,intent, entities):
        """
        Как обрабатывается default намерение, оно приходит от ТВИНА если он не понял намерение
        :param intent:
        :param entities:
        :return:
        """
        return random.choice(["Не понял Вас, повторите", "Что что? Повторите еще раз"])

    def on_twin_greeting(self, intent, entities):
        """
        Как бот обрабатывет приветствие twin_greeting
        :param intent:
        :param entities:
        :return:
        """
        phrases1 = ["Добрый день!","Здравствуйте!","Приветствую вас!"]
        phrases2 = ["Какой у вас вопрос?", "Меня зовут Тоша. Чем я могу помочь?",""]
        return "{p1} {p2}".format(p1 = random.choice(phrases1), p2 = random.choice(phrases2))

    def on_twin_goodbye(self, intent, entities):
        """
        Как бот обрабатывет когда с ним прощаются twin_goodbye
        :param intent:
        :param entities:
        :return:
        """
        return random.choice(["Всего доброго", "До свидания", "Всегда раз помочь"])

    def on_twin_repeat(self, intent, entities):
        """
        Как бот обрабатвает просьбу повторить twin_repeat
        :param intent:
        :param entities:
        :return:
        """
        return self.process(self.last_intent,self.last_entities)

class DialogTracker:
    """

    """
    def __init__(self,interpreter, action_handler):
        self.interpreter = interpreter
        self.action_handler = action_handler

    def predict(self, text: str) ->str:
        # парсим запрос
        intent, entities = self.interpreter.parse(text)
        # предсказываем ответ бота
        return self.action_handler.process(intent, entities)



if __name__ == "__main__":
    # интерпретатор фраз т.е. превразает фразу в намерение и сущности
    interpreter = TwinInterpreter()
    # обработчик ответов бота
    action_handler = ActionHandler()
    # сам диалог
    dialog = DialogTracker(interpreter = interpreter, action_handler=action_handler)
    while True:
        print("Вы:")
        input_text = input()
        output_text = dialog.predict(input_text)
        print("Бот:")
        print(output_text)
    pass