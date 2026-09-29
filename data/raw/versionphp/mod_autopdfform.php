<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Version file for Auto PDF Form activity module.
 *
 * @package    mod_autopdfform
 * @copyright  2025 Ivan Volosyak and Tangat Baktybergen <Ivan.Volosyak@@@hochschule-rhein-waal.de>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'mod_autopdfform';
$plugin->version   = 2025091500;
$plugin->requires  = 2022041900; // Moodle 4.0.
$plugin->cron      = 0;
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = 'v1.1';

// Optional hidden credit line.
$plugin->description = 'Auto PDF Form plugin for Moodle. Developed by Ivan Volosyak and Tangat Baktybergen, 2025.';
