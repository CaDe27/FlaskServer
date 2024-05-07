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

int generateRandomNumber(int min, int max) {
    return min + rand() % (max - min + 1);
}

std::string getCurrentDateStr() {
    auto now = std::chrono::system_clock::now();
    std::time_t timestamp = std::chrono::system_clock::to_time_t(now);
    std::tm tmTime = *std::localtime(&timestamp);

    std::ostringstream formattedDate;
    formattedDate << std::put_time(&tmTime, "%Y%m%d");
    return formattedDate.str();
}

int main() {
    // Seed the random number generator
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    // Open a file for writing the SQL statements
    std::ofstream sqlFile("serviceTests.sql");

    if (!sqlFile.is_open()) {
        std::cerr << "Failed to open the output file." << std::endl;
        return 1;
    }

    // Define the end time as four hours ago from the current time
    auto iterationTime = std::chrono::system_clock::now();

    // Iterate over the time range minute by minute
    std::string tableName = "http_requests";
    sqlFile << "INSERT INTO "<<tableName<<"(datetime, caller_service_id, receiver_service_id, status_code, latency_ms) VALUES "<< std::endl;
    int totalEdges;
    std::cin>>totalEdges;
    for(int i = 0; i < totalEdges; ++i){
        // Generate random values for caller_service_id, receiver_service_id, status_code, and latency_ms
        int callerServiceId = 1;
        int receiverServiceId = 2;
        int statusCode = 200;
        int latencyMs = 1;

        // Format the datetime in 'YYYY-MM-DD HH:MM:SS' format
        std::time_t timestamp = std::chrono::system_clock::to_time_t(iterationTime);
        std::tm tmTime = *std::localtime(&timestamp);
        std::ostringstream formattedDatetime;
        formattedDatetime << std::put_time(&tmTime, "%Y-%m-%d %H:%M:%S");

        // Generate the SQL INSERT statement
        
        sqlFile << "('" << formattedDatetime.str() << "', "
                << callerServiceId << ", " << receiverServiceId << ", " 
                << statusCode << ", " << latencyMs << ")" << (i==totalEdges-1? ";" : ",") <<std::endl;
    }

    // Close the output file
    sqlFile.close();

    std::cout << "SQL statements generated and saved to 'insert_statements.sql'." << std::endl;

    return 0;
}
