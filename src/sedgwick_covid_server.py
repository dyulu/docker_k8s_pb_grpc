#!/usr/bin/python3

from concurrent import futures
import logging
import os

import grpc

import sedgwick_covid_pb2
import sedgwick_covid_pb2_grpc

PORT = 50051

CovidCasesConfirmed = {}
def getData():
    data_path = os.path.dirname(os.path.realpath(__file__))
    try:
        with open('{}/sedgwick_covid.data'.format(data_path), 'r') as data_file:
            for line in data_file:
                line = line.strip()
                items = line.split(' ')
                if len(items) == 2:
                    CovidCasesConfirmed[str(items[0])] = int(items[1])
    except Exception as e:
        print(CovidCasesConfirmed)
        print("Error getting data: {}".format(e))
    print(CovidCasesConfirmed)

class CovidService(sedgwick_covid_pb2_grpc.CovidServiceServicer):
    def GetNumCasesConfirmed(self, request, context):
        if request.date not in CovidCasesConfirmed:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Data for date {} does not exist!!!'.format(request.date))
            return sedgwick_covid_pb2.CovidReply(date=request.date, num_cases_confirmed=-1)
        return sedgwick_covid_pb2.CovidReply(date=request.date, num_cases_confirmed=CovidCasesConfirmed[request.date])

    def GetAll(self, request, context):
        for date in CovidCasesConfirmed:
            yield sedgwick_covid_pb2.CovidReply(date=date, num_cases_confirmed=CovidCasesConfirmed[date])

    def GetTotal(self, request_iterator, context):
        total = 0
        dates = []
        for request in request_iterator:
            if request.date in CovidCasesConfirmed:
                total += CovidCasesConfirmed[request.date]
            dates.append(request.date)
        return sedgwick_covid_pb2.CovidReply(date=','.join(dates), num_cases_confirmed=total)

    def GetNumCasesConfirmedForDates(self, request_iterator, context):
        for request in request_iterator:
            yield self.GetNumCasesConfirmed(request, context)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sedgwick_covid_pb2_grpc.add_CovidServiceServicer_to_server(CovidService(),  server)
    server.add_insecure_port('[::]:{}'.format(PORT))
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    getData()
    serve()


