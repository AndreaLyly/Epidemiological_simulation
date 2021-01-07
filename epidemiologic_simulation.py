import pygame
import time
import random
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from sklearn.linear_model import LinearRegression
import numpy as np

random.seed(23)

pygame.init()

size = width, height = 500, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

white = (255,255,255)
red   = (255,0,0)
green = (0,128,0)
black = (0,0,0)
blue  = (0,0,255)

w           = 10            # individual size
n           = 200           # population size
speed       = 10            # movement speed normal
speedsick   = 9             # movement speed sick
simuspeed   = 50            # simulation speed
sick_time   = 70            # average time of being sick 
infect      = 2             # number of initial sick people
delay       = (0, 5)        # delay to being sick after contact
vaccinated  = int(n * 0)    # percentage vaccinated
Recov_carry = False
threshold = 0.5 # threshold level of getting infected

## Class Object for people in simulation world
class Obj:
    def __init__(self, xs, ys, sp, ss, a):
        self.x = xs
        self.y = ys
        self.speed = sp
        self.speedsick = ss
        self.rect = pygame.rect.Rect((xs, ys, w, w))
        self.susc  = True
        self.infec = False
        self.recov = False
        self.dead  = False
        self.vacc  = False
        self.sick = 0
        self.time_sick = sick_time #random.randint(sick_time[0], sick_time[1])
        self.trigger = False
        self.triggerTime = 0
        self.temp = 0

    def draw(self, screen):
        if self.susc == True:
            pygame.draw.rect(screen, white, self.rect)
        elif self.infec == True:
            pygame.draw.rect(screen, red, self.rect)
        elif self.recov == True:
            pygame.draw.rect(screen, green, self.rect)
        elif self.dead == True:
            pygame.draw.rect(screen, black, self.rect)
        elif self.vacc == True:
            pygame.draw.rect(screen, blue, self.rect)

    def move(self):
        if self.infec == True:
            s = self.speedsick
        else:
            s = self.speed

        (deltax, deltay) = random.choice([(0, s), (0, -s), (s, 0), (-s, 0)])
        self.x = self.x + deltax
        self.y = self.y + deltay

        if self.x > width + w:
            self.x = 0 
        elif self.x < 0 - w:
            self.x = width-w
        elif self.y > height + w:
            self.y = 0 - w 
        elif self.y < 0 - w:
            self.y = height - w
        self.rect = pygame.rect.Rect((self.x, self.y, w, w))

    def infected(self):
        if self.trigger == True:
            self.temp += 1
            if self.temp > self.triggerTime:
                self.infec = True
                self.temp = 0
                self.trigger = False
        elif self.infec == True:
            self.susc = False
            self.sick += 1
            #prob_dead = random.random()
            if self.sick == self.time_sick:
                self.recov = True
                self.infec = False
                self.sick = 0
            #elif prob_dead < 0.0001:
            #    self.dead  = True
            #    self.infec = False
            #    self.speed = 0

# Vaccinate a certain number of people
def vaccinate(popu, N):
    for i in range(N):
        if popu[i].infec != True:
            popu[i].vacc = True
            popu[i].susc = False

# Random position function
def random_pos():
    x = random.randint(0, width)
    y = random.randint(0, height) 
    return (x,y)

# Results of the simulation world
def results(s, i, r, d, t, c):

    S0, I0, R0 = s[0], i[0], r[0]

    evtime = 55
    tt = np.array(t[0:evtime])
    logi = np.log(np.array(i))[0:evtime]

    model = LinearRegression().fit(tt.reshape((-1,1)), logi)
    
    beta = model.coef_[0]
    gamma = 1 / (sick_time)

    def system(y, t, beta, gamma, N):
        S, I, R = y
        dsdt = -beta/N * S * I 
        didt = beta/N * S * I - gamma * I
        drdt = gamma * I
        return dsdt, didt, drdt
    
    y0 = S0, I0, R0
    res = odeint(system, y0, t, args=(beta, gamma, n))
    S, I, R = res.T

    plt.figure()
    plt.plot(t,s, color="blue")
    plt.plot(t,i, color="red")
    plt.plot(t,r, color="green")

    plt.plot(t,S, 'b--')
    plt.plot(t,I, 'r--')
    plt.plot(t,R, 'g--')

    plt.xlabel("Time")
    plt.ylabel("Number in groups")
    plt.legend(["Susceptible", "Infected", "Recovered", "S-Model", "I-Model", "R-Model"])
    plt.title("Simulation world results")

    plt.show()


# The simulation function
def simu_loop():
    time  = [0]         # time count
    Slist = [n-infect]  # initial number of susceptible
    Ilist = [infect]    # initial number of infected
    Rlist = [0]         # initial number of recovered
    Dlist = [0]         # initial number of dead
    plist = []          # object list
    count = []
    for i in range(n):
        pos = random_pos()
        age = random.randint(5,90)
        p = Obj(pos[0], pos[1], speed, speedsick, age)
        plist.append(p)

    #vaccinate(plist, vaccinated)

    for ind in range(infect):
        plist[ind].infec = True

    # Simulation loop
    simulation_end = False
    while not simulation_end:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        screen.fill((0,30,50))
        for i in plist:
            i.move()
            i.draw(screen)
            i.infected()
            for j in plist:
                if i != j:
                    dx = abs(i.x - j.x)     # x position difference
                    dy = abs(i.y - j.y)     # y position difference
                    prob = random.random()  # probability of infection
                    if i.infec == True and j.susc == True and j.vacc != True and dx < 10 and dy < 10 and prob > threshold:
                        #j.infec = True
                        j.trigger = True
                        j.triggerTime = random.randint(delay[0],delay[1])


        time.append(time[-1]+1)
        #if time[-1] == 30:
        #    for ind in range(infect):
        #        plist[ind].infec = True

        S = sum(map(lambda x : x.susc  == True, plist))
        I = sum(map(lambda x : x.infec == True, plist))
        R = sum(map(lambda x : x.recov == True, plist))
        D = sum(map(lambda x : x.dead  == True, plist))
        Slist.append(S)
        Ilist.append(I)
        Rlist.append(R)
        Dlist.append(D)

        if I == 0 and time[-1] > 200:
            simulation_end = True
            print(count)
            results(Slist, Ilist, Rlist, Dlist, time, count)

        pygame.display.update()
        clock.tick(simuspeed)


if __name__ == "__main__":
    simu_loop()
