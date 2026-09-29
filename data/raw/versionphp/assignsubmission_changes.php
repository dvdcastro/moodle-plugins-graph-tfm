<?php
// This file is part of AssignSubmission_Changes plugin for Moodle - http://moodle.org/
//
// AssignSubmission_Changes is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// AssignSubmission_Changes is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with AssignSubmission_Changes.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Assign Submission Changes
 *
 * @package   assignsubmission_changes
 * @author    Hendrik Wuerz <[email]>
 * @copyright (c) 2017 Hendrik Wuerz
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die;

global $CFG;


$plugin->component = 'assignsubmission_changes';

// Require the backup and compare libs.
$plugin->dependencies = array(
    'local_changeloglib' => 2017123100,
);


$plugin->release = '0.2.2';
$plugin->maturity = MATURITY_ALPHA;
$plugin->cron = 1;

// Version format:  YYYYMMDDXX .
$plugin->version = 2017123100;
$plugin->requires = 2017051500;