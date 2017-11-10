'use strict';

/**
 * Material Accordion constructor.
 * @param {object} element The DOM element.
 * @constructor
 */
var MaterialAccordion = function(element) {
  this.element_ = element;
  this.init();
};

/**
 * The CSS classes used in Material Accordion.
 * @enum {string}
 * @private
 */
MaterialAccordion.prototype.CssClasses_ = {
  HEADING: 'mdl-collapse__button',
  CONTENT: 'mdl-collapse__content',
  CONTENT_WRAPPER: 'mdl-collapse__content-wrapper',
  IS_OPENED: 'mdl-collapse--opened',
  IS_UPGRADED: 'is-upgraded'
};

/**
 * Handles the onclick event for Material Accordion.
 * @private
 */
MaterialAccordion.prototype.onClick_ = function() {
  this.element_.classList.toggle(this.CssClasses_.IS_OPENED);
};

/**
 * Initializes this instance of Material Accordion.
 */
MaterialAccordion.prototype.init = function() {
  if (this.element_) {
    this.heading_ = this.element_.querySelector('.' + this.CssClasses_.HEADING);
    this.content_ = this.element_.querySelector('.' + this.CssClasses_.CONTENT);
    this.content_wrapper_ =
        this.element_.querySelector('.' + this.CssClasses_.CONTENT_WRAPPER);

    this.boundClickHandler = this.onClick_.bind(this);
    this.heading_.addEventListener('click', this.boundClickHandler);

    this.element_.classList.add(this.CssClasses_.IS_UPGRADED);

    // set margin-top after DOM has been rendered
    setTimeout(function() {
      this.content_wrapper_.style.display = 'block';
    }.bind(this), 0);
  }
};

componentHandler.register({
  constructor: MaterialAccordion,
  classAsString: 'MaterialAccordion',
  cssClass: 'mdl-js-accordion',
  widget: true
});
