var ViewModel = function() {
  var self = this;
  this.clickCount = ko.observable(0);
  this.name = ko.observable("Tabby");
  this.imgSrc = ko.observable("img/434164568_fea0ad4013_z.jpg");
  this.imgAttribution = ko.observable("https://www.flickr.com/photos/big");
  this.catLevel = ko.computed(function() {
    if (self.clickCount() < 10) {
      return "Newborn";
    } else if (self.clickCount() < 100) {
      return "Infant";
    } else {
      return "Teen";
    }
  });

  this.incrementCounter = function() {
    this.clickCount(this.clickCount() + 1);
  };
};

ko.applyBindings(new ViewModel());
