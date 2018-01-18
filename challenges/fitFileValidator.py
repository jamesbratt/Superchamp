import operator
import datetime
import time
import json

from routes.models import Route

from django.contrib.gis.geos import LineString, Point

from fitparse import FitFile
from polyline.codec import PolylineCodec


class AnalytseFile():
    def Validate(self, fileInMemory, rideId):
        AttemptCoordsOne = []
        AttemptCoordsTwo = []
        raceCoords = []
        fitStartTime = None

        fitfile = FitFile(fileInMemory)

        for session in fitfile.get_messages('session'):
            sessionVals = session.get_values()
            fitStartTime = sessionVals['start_time']

        ride = Route.objects.get(pk=rideId)

        race = ride.polyline
        DecodedRace = PolylineCodec().decode(race)

        for coord in DecodedRace:
            raceCoords.append((coord[1], coord[0]))

        raceRoute = LineString(raceCoords, srid=4326)

        for record in fitfile.get_messages('record'):
            lat = record.get_value('position_lat')
            lng = record.get_value('position_long')
            time = record.get_value('timestamp')
            speed = record.get_value('speed')
            distance = record.get_value('distance')
            elevation = record.get_value('altitude')

            if lng is not None or lat is not None:
                nlng = lng * (180.0/2**31)
                nlat = lat * (180.0/2**31)
                AttemptCoordsOne.append((nlng, nlat))
                AttemptCoordsTwo.append({'distance': distance, 'time': time, 'speed': speed, 'elevation': elevation, 'position': (nlng, nlat)})

        rideGeom = LineString(AttemptCoordsOne, srid=4326)
        rideGeomBuffer = rideGeom.buffer(0.0005)

        # First check if the actual ride intersects with the
        # ser route and return the intersected route as a linestring
        # in case the rider has taken a wrong turn
        # and had to go back on themselves
        CheckIntersects = rideGeomBuffer.intersection(raceRoute)

        # Now create a buffer geom of the set route
        # and check whether it contains the intersected route
        racerouteGeomBuffer = raceRoute.buffer(0.0005)
        CheckMatch = racerouteGeomBuffer.contains(CheckIntersects)

        if CheckMatch is True:
            ClosestPoints = []
            ClosestLists = []

            raceBuffer = raceRoute.buffer(0.0001)
            refPoints = [(float(ride.start_long), float(ride.start_lat)), (float(ride.finish_long), float(ride.finish_lat))]

            for ref in refPoints:
                proximityPoint = None
                RacePointGeom = Point(ref, srid=4326)
                numbers = [self.distance(AttemptCoord, RacePointGeom) for AttemptCoord in AttemptCoordsTwo]
                sortedList = sorted(numbers, key=operator.itemgetter(1))

                for s in sortedList:
                    sGeom = Point(s[0], srid=4326)
                    CheckIsInRoute = raceBuffer.contains(sGeom)
                    if CheckIsInRoute is True:
                        proximityCheck = self.pointTooClose(ref, s[0])
                        if proximityCheck is True:
                            sortedList.remove(s)
                        else:
                            proximityPoint = s
                            break

                ClosestLists.append(sortedList)
                ClosestPoints.append(proximityPoint)

            # Creating a json blob with all the interesting gps data
            json_data = []
            for json_position in AttemptCoordsTwo:
                json_point = Point(json_position['position'], srid=4326)
                CheckJsonIsInRoute = raceBuffer.contains(json_point)

                if CheckJsonIsInRoute is True:
                    obj = self.GenerateJsonObject(json_position)
                    json_data.append(obj)

            # Conditional to handle when ride goes back on itself
            if ClosestPoints[0][2] > ClosestPoints[1][2]:
                return 'reverse'
            else:
                TimeDiff = ClosestPoints[1][2] - ClosestPoints[0][2]

                avRaceSpeed = self.CalculateAverageRaceSpeed(TimeDiff, ride.distance)
                startTimeCheck = self.checkDiscrepencies(ClosestPoints, TimeDiff, refPoints[0], 'start', avRaceSpeed)
                FinalTime = self.checkDiscrepencies(ClosestPoints, startTimeCheck, refPoints[1], 'finish', avRaceSpeed)
                totalAvSpeed = self.CalculateAverageRaceSpeed(FinalTime, ride.distance)
                av_speed_converted = (totalAvSpeed * 60 * 60)/1000  # Convert meters per second to km per hour
                return {'duration': FinalTime, 'start_time': fitStartTime, 'average_speed': round(av_speed_converted, 1), 'data': json.dumps(json_data)}
        else:
            return False

    def GenerateJsonObject(self, position):
        obj = {}
        obj['latitude'] = position['position'][0]
        obj['longitude'] = position['position'][1]
        obj['time'] = position['time'].strftime('%Y-%m-%d %H:%M:%S')
        obj['speed'] = (position['speed'] * 60 * 60)/1000
        obj['elevation'] = position['elevation']

        return obj

    def CalculateAverageRaceSpeed(self, time, distance):
        d = distance*1000
        avSpeed = d/time.total_seconds()
        return avSpeed

    def pointTooClose(self, refPoint, closestPoint):
        refGeom = Point(refPoint, srid=4326).transform(3857, clone=True)
        closestGeom = Point(closestPoint, srid=4326).transform(3857, clone=True)

        dist = refGeom.distance(closestGeom)
        if dist < 20:
            return True
        else:
            return False

    def distance(self, point, ref):
        p = Point(point['position'], srid=4326)
        dist = p.distance(ref)
        resp = (point['position'], dist, point['time'], point['speed'], point['elevation'])
        return resp

    def checkDiscrepencies(self, ClosestPoints, TimeDiff, refPoints, flag, avRaceSpeed):
        # Start/End point of race
        A = Point(refPoints, srid=4326).transform(3857, clone=True)

        # The closest coordinate to the start/end point
        if flag == 'start':
            B = Point(ClosestPoints[0][0], srid=4326).transform(3857, clone=True)
        else:
            B = Point(ClosestPoints[1][0], srid=4326).transform(3857, clone=True)

        # Work out distance between the start/end point and its's closest point
        ABd = A.distance(B)

        # Time taken to ride between start/end point and the closest point
        startToClosestTimeTaken = ABd/avRaceSpeed

        # Round up time taken
        secs = int(round(startToClosestTimeTaken))
        return TimeDiff + datetime.timedelta(seconds=secs)
