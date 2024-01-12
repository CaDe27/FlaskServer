/*
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    datetime TIMESTAMP NOT NULL,
    caller_service_id INT,
    receiver_service_id INT,
    status_code INT,
    latency_ms INT,
*/
#include <iostream>
#include <fstream>
#include <ctime>
#include <cstdlib>
#include <chrono>
#include <iomanip>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <string>
using namespace std;

void loadAdj(vector<pair<int, float> > *adj){
    adj[0].push_back(pair(1, 0.3));
    adj[0].push_back(pair(2, 0.3));
    adj[0].push_back(pair(3, 0.3));
    adj[1].push_back(pair(4, 0.5));
    adj[2].push_back(pair(3, 0.8));
    adj[2].push_back(pair(4, 0.8));
    adj[2].push_back(pair(5, 0.8));
    adj[3].push_back(pair(0, 0.3));
    adj[5].push_back(pair(9, 0.3));
    adj[6].push_back(pair(0, 0.6));
    adj[6].push_back(pair(1, 0.6));
    adj[6].push_back(pair(2, 0.6));
    adj[6].push_back(pair(4, 0.6));
    adj[7].push_back(pair(1, 0.2));
    adj[8].push_back(pair(1, 0.3));
    adj[8].push_back(pair(4, 0.3));
    adj[8].push_back(pair(7, 0.3));
    adj[10].push_back(pair(0, 0.6));
    adj[10].push_back(pair(1, 0.6));
    adj[10].push_back(pair(2, 0.6));
    adj[10].push_back(pair(3, 0.6));
    adj[10].push_back(pair(4, 0.6));
    adj[10].push_back(pair(5, 0.6));
    adj[10].push_back(pair(6, 0.6));
    adj[10].push_back(pair(7, 0.6));
    adj[10].push_back(pair(8, 0.6));
    adj[10].push_back(pair(9, 0.6));
}

int generateRandomNumber(int min, int max) {
    return min + rand() % (max - min + 1);
}

float randomNumber0To1(){
    return ((float)rand())/RAND_MAX;
}

int main() {
    // Seed the random number generator
    srand(static_cast<unsigned int>(time(nullptr)));

    // Open a file for writing the SQL statements
    ofstream sqlFile("dummyRequestsInsertion.sql");

    // Get the current time
    auto endTime = chrono::system_clock::now() - chrono::hours(48);
    vector<pair<int, float> > adj[11];
    loadAdj(adj);
    unordered_map<int, string> services_dict = {
        {1, "Users"},
        {2, "Products"},
        {3, "Orders"}, 
        {4, "Payments"}, 
        {5, "Inventory"},
        {6, "Shipping"},
        {7, "Recommendations"},
        {8, "Reviews"}, 
        {9, "Promotions"}, 
        {10, "Notifications"},
        {11, "Analytics"}
    };

    // Iterate over the time range minute by minute
    string tableName = "http_requests";
    sqlFile << "INSERT INTO "<<tableName<<"(datetime, caller_service_id, receiver_service_id, status_code, latency_ms) VALUES "<< endl;
    for(auto iterationTime = endTime - chrono::hours(24); iterationTime <= endTime; iterationTime += chrono::minutes(1)) {
    for(int i = 0; i < 1; ++i){
        for(int callerServiceId = 0; callerServiceId < 11; ++callerServiceId){
        for(pair<int, float> receiverInfo : adj[callerServiceId]){
            int receiverServiceId = receiverInfo.first;
            float probability = receiverInfo.second;
            if( randomNumber0To1() < probability){
                float num = randomNumber0To1();
                int statusCode, latencyMs;
                if(num < 0.05){
                    statusCode = generateRandomNumber(100, 199);
                    latencyMs = generateRandomNumber(0, 10);
                }
                else if(num < 0.6){
                    statusCode = generateRandomNumber(200, 299);
                    latencyMs = generateRandomNumber(0, 100);
                }
                else if(num < 0.8){
                    statusCode = generateRandomNumber(300, 399);
                    latencyMs = generateRandomNumber(0, 100);
                }
                else if(num < 0.9){
                    statusCode = generateRandomNumber(400, 499);
                    latencyMs = generateRandomNumber(0, 500);
                }
                else{
                    statusCode = generateRandomNumber(500, 599);
                    latencyMs = generateRandomNumber(0, 500);
                }
                
                // Format the datetime in 'YYYY-MM-DD HH:MM:SS' format
                time_t timestamp = chrono::system_clock::to_time_t(iterationTime);
                tm tmTime = *localtime(&timestamp);
                ostringstream formattedDatetime;
                formattedDatetime << put_time(&tmTime, "%Y-%m-%d %H:%M:%S");

                sqlFile << "('" << formattedDatetime.str() << "', "
                    << (1+callerServiceId) << ", " << (1+receiverServiceId) << ", " 
                    << statusCode << ", " << latencyMs << ")," <<endl;

                ofstream logFile("logs/"+services_dict[receiverServiceId+1]+"-received_requests.txt", ios::app);
                logFile << formattedDatetime.str() <<" - from: "<<services_dict[1+callerServiceId]<<" - status code: "<< statusCode << " - latency (ms): "<<latencyMs<<"\n";
                logFile.close();
            }
        }
        }
    }
    }
    // Close the output file
    sqlFile.close();

    cout << "SQL statements generated and saved to 'insert_statements.sql'." << endl;

    return 0;
}
