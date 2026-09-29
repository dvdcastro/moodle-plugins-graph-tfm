<?php

/**
 * Version details
 *
 * @package    block
 */

$plugin->release   = '1.0';
$plugin->version   = 2013010900;        // The current plugin version (Date: YYYYMMDDXX)
$plugin->requires  = 2012112900;        // Requires this Moodle version
$plugin->component = 'local_jquery';

global $PAGE;
$PAGE->requires->js('/local/jquery/jquery-1.8.3.min.js', true);
