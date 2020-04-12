#!/usr/bin/python3

from __future__ import print_function
import logging
import os

import grpc

import sedgwick_covid_pb2
import sedgwick_covid_pb2_grpc

def print_responses(responses):
    for response in responses:
        print("Number of confirmed cases on date {}: {}".format(response.date, response.num_cases_confirmed))

def generate_covid_request_iterator(dates):
    for date in dates:
        yield sedgwick_covid_pb2.CovidRequest(date=date)

def run(logger):
    COVID_SERVER = os.getenv('COVID_SERVER')
    if COVID_SERVER == None:
        COVID_SERVER = "covid_server"
    COVID_PORT = os.getenv('COVID_PORT')
    if COVID_PORT == None:
        COVID_PORT = 50051
    covid_channel = "{}:{}".format(COVID_SERVER, COVID_PORT)
    logger.info("covid_channel: {}".format(covid_channel))

    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel(covid_channel) as channel:
        stub = sedgwick_covid_pb2_grpc.CovidServiceStub(channel)
        while True:
            date_input = input("Enter date in mmddyyyy[,mmddyyyy...] or mmddyyyy[+mmddyyyy...] or all to get all or return to quit: ")
            if not date_input:
                logger.warning("User did not enter a date, so quitting...")
                break
            try:
                logger.debug("User entered date {}".format(date_input))
                if date_input == 'all':
                    responses = stub.GetAll(sedgwick_covid_pb2.GetAllRequest())
                    print_responses(responses)
                elif "," in date_input:
                    dates = date_input.split(",")
                    covid_request_iterator = generate_covid_request_iterator(dates)
                    responses = stub.GetNumCasesConfirmedForDates(covid_request_iterator)
                    print_responses(responses)
                elif "+" in date_input:
                    dates = date_input.split("+")
                    covid_request_iterator = generate_covid_request_iterator(dates)
                    response = stub.GetTotal(covid_request_iterator)
                    responses = [response]
                    print_responses(responses)
                else:
                    response = stub.GetNumCasesConfirmed(sedgwick_covid_pb2.CovidRequest(date=date_input))
                    responses = [response]
                    print_responses(responses)
            except grpc.RpcError as e:
                logger.critical("grpc.RpcError: {}".format(e))
                if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                    print("    {}".format(e.details()))
                else:
                    print("    Exception {} getting data for date {}".format(e, date_input))

if __name__ == '__main__':
    logging.basicConfig(filename="covid_client.log", format='%(asctime)s %(message)s', filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    run(logger)

