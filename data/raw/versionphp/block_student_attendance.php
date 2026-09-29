<?php
defined('MOODLE_INTERNAL') || die();

$plugin->component    = 'block_student_attendance';
$plugin->version      = 2026051000;
$plugin->requires     = 2022041900; // Moodle 4.0+
$plugin->maturity     = MATURITY_STABLE;
$plugin->release      = '1.1.0';
$plugin->dependencies = ['mod_attendance' => 2022041900];
