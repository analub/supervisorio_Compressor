from db import Session, create_database
from models import CompData
from queue import Queue
from threading import Lock

#colocar estes métodos dentro do init
self._db_queue = Queue()
self._db_lock = Lock()
create_database() #criar a tabela do BD

#Lógica para ser implementada dentro da função updater no mainwidget.py
def updater(self):
    try:
        while self._updateWidgets:
            self.readData()
            self.updateGUI()

            # Envia os dados para a fila do banco
            self._db_queue.put(self._meas.copy()) #faz a copia da leitura e coloca na fila
            #não usa meas direto pois ele pode ser atualizado equanto a gravação está sendo feita

            sleep(self._scan_time/1000)
    except Exception as e:
        self._modbusClient.close()
        print("Erro: ", e.args)

#adicionar essa função no mainwidget.py para gravação no BD
def db_writer(self):
    session = Session()
    while self._updateWidgets:
        try:
            data = self._db_queue.get() #só entra no modo de gravação se tiver dado disponível pra gravar
            if data is None:
                break

            values = data['values']

            row = ProcessData(
                timestamp=data['timestamp'],
                **{k: values.get(k) for k in values}
            )

            with self._db_lock:
                session.add(row)
                session.commit()

        except Exception as e:
            session.rollback()
            print("Erro ao salvar no banco:", e)

    session.close()

#dentro do método startDataRead(), incluir:
self._updateThread = Thread(target=self.updater)
self._updateThread.start()

self._dbThread = Thread(target=self.db_writer)
self._dbThread.start()
