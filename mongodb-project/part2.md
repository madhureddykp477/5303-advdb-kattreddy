###Part 2: Queries on the data in mongodb.

##Names: Vishnu Chaitanya Mandalapu, Madhuchirra Reddy Kattreddy

#
1.	db.yelp.business.find({$or: [{"full_address" : {$regex : ".*89117.*"}},{"full_address" : {$regex : ".*89122.*"}}]}).count()

2.	db.yelp.business.find({"full_address": {$regex: ".*Las Vegas.*"}}).count()

3.	 db.yelp.business.find({ "loc" : { $geoWithin : { $centerSphere: [ [ -80.839186, 35.226504 ], 5 / 3963.2 ] } } }).count()

4.	db.yelp.review.find({"business_id" : "hB3kH0NgM5LkEWMnMMDnHw")}).count()


5.	db.yelp.review.find({ $and : [{"business_id" : "P1fJb2WQ1mXoiudj8UE44w"}, {"stars" : 5}]}).count()

6.	db.yelp.user.find({ "yelping_since" : {$lte:"2011-11"}}).count()

7.	db.yelp.tip.find().sort({"likes":-1}).limit(1).pretty()

8.	db.yelp.user.aggregate([{$group:{_id:"review_count",averageReviewCount:{$avg:"$review_count"}}}])

9.	db.yelp.user.find({"elite":{"$ne":[]}},{"_id":0,"user_id":1,"name":1,"elite":1})

10.	db.yelp.user.find({"elite":{"$ne":[]}}).sort({"elite":-1}).limit(1)

11.	db.yelp.user.aggregate({$project: {elitelength:{$size:"$elite"}}},{$group:{_id:0, avg:{$avg:"$elitelength"}}})

------------Difficult Queries--------------

12.	var review_result = db.yelp.review.find({"user_id":"xOQVHYN1roRZKpLvAT-a2A"},{"business_id":1})
	  db.yelp.business.find({"business_id":review_result},{"city":1})

13.	db.yelp.business.find({$or: [{"full_address" : {$regex : ".*75205.*"}},{"full_address" : {$regex : ".*75225.*"}}]})
	Returns an empty set, which means there is no restaurant in these locations.

14.	db.yelp.checkin.find({"checkin_info":{$lte:"2-0",$gte:"17-5"}},{"business_id":1}).pretty()

15.	db.yelp.review.aggregate([{$match:{business_id:"mVHrayjG3uZ_RLHkLj-AMg"}},{$group:{_id:'$stars', count:{$sum:1}}}])

16.	db.yelp.review.aggregate([{$group:{_id: "$business_id", avgstar:{$avg:"$stars"}}},{$match: {avgstar:{$gt:3.5}}}])
