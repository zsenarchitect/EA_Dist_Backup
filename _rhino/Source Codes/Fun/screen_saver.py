import rhinoscriptsyntax as rs
import scriptcontext as sc

import Rhino # pyright: ignore
import random
import math

import threading
import sys
sys.path.append("..\lib")
import EnneadTab

NAME_TAG = "EnneadTab_screen_saver_objs"

#must inherate object, cannot ignore, otherwise the super() will not work for the childs
class Agent(object):
    def __init__(self, universe, guid = None):
        self.name_tag = NAME_TAG
        self.life_span = -1
        self.mass = 0
        self.color = rs.CreateColor([random.random() * 256,
                                    random.random() * 256,
                                    random.random() * 256])
        
        self.guid = guid
        if self.guid:
            rs.ObjectColor(self.guid, self.color)
            rs.ObjectName(self.guid, self.name_tag)
            
        Agent.universe = universe

    
    def force_collector(self, search_radius):
        force = Rhino.Geometry.Vector3d(0,0,0)
        
        for item in Agent.universe.collection:
            if item.guid == self.guid:
                continue
            dist = rs.Distance(item.location, self.location)
            if dist > search_radius:
                continue
            
            temp_force_magnitude = (item.mass * self.mass) / (dist*dist)
            temp_force_direction = Rhino.Geometry.Vector3d(self.location- item.location)
            temp_force = temp_force_magnitude * temp_force_direction
            force += temp_force
            
        return force
        
    
    def get_acceleration(self, search_radius = 200):
        
        
        return self.force_collector(search_radius)/ self.mass
    
    
    
    
class Planet(Agent):
    def __init__(self, universe):
        self.location = Rhino.Geometry.Point3d(random.random() * 20,
                                                random.random() * 20,
                                                random.random() * 20)
        self.obj_r = random.random() * 2
     
        super(Planet, self).__init__(universe,guid = rs.AddSphere(self.location, self.obj_r))
        
        self.mass = 1000

    def update(self, current_frame):
        # rs.DeleteObject(self.guid)
        
        self.obj_r += math.sin(current_frame)
        
        sc.doc.Objects.Replace(self.guid, Rhino.Geometry.Sphere(self.location,
                                                               self.obj_r).ToNurbsSurface())
        
        
class Rocket(Agent):
    def __init__(self, universe):
        self.location = Rhino.Geometry.Point3d(random.random() * 20,
                                                random.random() * 20,
                                                random.random() * 20)
        pointy_direction = Rhino.Geometry.Vector3d(0,0,1)
        plane = Rhino.Geometry.Plane(self.location, pointy_direction)
        super(Rocket, self).__init__(universe,
                                    guid = rs.AddCone(plane,
                                                       1,
                                                       2))
        self.trails = []
        self.velocity = Rhino.Geometry.Vector3d(random.random() * 20,
                                                random.random() * 20,
                                                random.random() * 20)
        self.mass = 100
        
        
    def update(self, current_frame):
        # move self
        acceleration = self.get_acceleration()
        self.location += self.velocity + acceleration
        
  
        
        
        # update all the trailirs
        for trail in self.trails:
            trail.update(current_frame)

            if trail.is_dead:
                self.trails.remove(trail)
                
        self.trails.append(Trail(Agent.universe, self.location))
        

class Trail(Agent):
    def __init__(self, universe, born_place):
        self.life_span = 10
        self.location = born_place
        super(Trail, self).__init__(universe, guid= rs.AddPoint(self.location))
        
    @property
    def is_dead(self):
        return self.life_span <= 0
    
    def update(self, current_frame):
        self.life_span -= 1
        
        #fall by gravity
        
        pass
        
class Universe(object):
    def __init__(self):
        self.is_stopped = False
        self.is_loop = False
  
        self.screen_saver_life_span = 30
        self.interval = 0.5 # every 0.5 second
        self.max_frame = self.screen_saver_life_span / self.interval
        self.current_frame = 0
        self.timer = None
        self.show_progress = True
        
        self.setup()

    def setup(self):
        
        old_objs = rs.ObjectsByName(NAME_TAG)
        if old_objs:
            rs.DeleteObjects(old_objs)
            
            
        self.collection = [ Planet(self),Rocket(self),Rocket(self)]
        rs.ObjectColorSource([x.guid for x in self.collection], 1)
    
    
    
    def update(self):
#        print self.collection
        map(lambda x: x.update(self.current_frame) , self.collection)
  



    def on_timed_event(self):
        self.current_frame += 1
        
       
        self.update()

        if self.current_frame < self.max_frame:

            self.timer = threading.Timer(self.interval, self.on_timed_event)
            self.timer.start()
        else:
            if self.is_loop:
                self.current_frame = 0
            else:
                print("Timer stopped after", self.screen_saver_life_span, "seconds")
                self.stop_timer()
  
        
        
        
        if self.show_progress:
            rs.StatusBarProgressMeterUpdate(position=self.current_frame)
            # print ("{}/{}".format(int(self.current_frame), int(self.max_frame )))



    def stop_timer(self):
        self.timer.cancel()
        if self.show_progress:
            rs.StatusBarProgressMeterHide()

    def begin(self):
        print("Timer begins!")
        if self.show_progress:
            rs.StatusBarProgressMeterShow(label = "Screen Saver",
                                          lower=0,
                                          upper=self.max_frame)
        self.timer = threading.Timer(self.interval, self.on_timed_event)
        self.timer.start()  


#@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    Universe().begin()
    
    
##############################


if __name__ == "__main__":
    main()