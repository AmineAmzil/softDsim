import { Flex, FormControl, Grid, Switch, Tooltip } from '@chakra-ui/react'
import React, { useState, useEffect } from 'react'
import ActionSlider from './ActionSlider'
import ActionToggle from './ActionToggle'
import ActionSelect from './ActionSelect'
import { actionIcon } from "../../ScenarionStudio/scenarioStudioData"
import ActionElement from "./ActionElement";
import { FaQuestionCircle } from 'react-icons/fa';


const Action = (props) => {
    const [activeTooltip, setActiveTooltip] = useState(null);

    useEffect(() => {
        const handleDocumentClick = (event) => {
            if (activeTooltip && !event.target.closest('.tooltip-container')) {
                setActiveTooltip(null);
            }
        };

        document.addEventListener('click', handleDocumentClick);

        return () => {
            document.removeEventListener('click', handleDocumentClick);
        };
    }, [activeTooltip]);

    const handleButtonClick = (tooltip) => {
        setActiveTooltip(tooltip);
    };

    if (Object.keys(props).length > 0) {
        return (
            <Grid borderRadius="xl">
                {props.action.action === 'bugfix' ? (
                    <ActionElement
                        title={
                            <div style={{display: 'flex', alignItems: 'center'}}>
                                Bugfixing
                                <div className="tooltip-container" style={{marginLeft: '8px'}}>
                                    <Tooltip
                                        label="Fix known bugs. Bugs are discovered after unit testing"
                                        isOpen={activeTooltip === 'bugfix'}
                                    >
                                        <button onClick={() => handleButtonClick('bugfix')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Start Bugfixing"
                        icon={actionIcon.BUGFIX}
                    >
                        <FormControl display="flex" justifyContent="end">
                            <Switch
                                onChange={(event) =>
                                    props.onSelectAction({
                                        type: props.action.action,
                                        value: event.target.checked
                                    })
                                }
                                size="lg"
                                defaultChecked={props.actionDefaultValues.bugfix}
                            />
                        </FormControl>
                    </ActionElement>
                ) : props.action.action === 'unittest' ? (
                    <ActionElement
                        title={
                            <div style={{display: 'flex', alignItems: 'center'}}>
                                Unit Testing
                                <div className="tooltip-container" style={{marginLeft: '8px'}}>
                                    <Tooltip
                                        label="Test specific parts for functionality and/or bugs"
                                        isOpen={activeTooltip === 'unittest'}
                                    >
                                        <button onClick={() => handleButtonClick('unittest')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Start Unit Testing"
                        icon={actionIcon.UNITTEST}
                    >
                        <FormControl display="flex" justifyContent="end">
                            <Switch
                                onChange={(event) =>
                                    props.onSelectAction({
                                        type: props.action.action,
                                        value: event.target.checked
                                    })
                                }
                                size="lg"
                                defaultChecked={props.actionDefaultValues.unittest}
                            />
                        </FormControl>
                    </ActionElement>
                ) : props.action.action === 'integrationtest' ? (
                    <ActionElement
                        title={
                            <div style={{display: 'flex', alignItems: 'center'}}>
                                Integration Testing
                                <div className="tooltip-container" style={{marginLeft: '8px'}}>
                                    <Tooltip
                                        label="Integration testing should be done after unit testing and bug fixing"
                                        isOpen={activeTooltip === 'integrationtest'}
                                    >
                                        <button onClick={() => handleButtonClick('integrationtest')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Start Integration Testing"
                        icon={actionIcon.INTEGRATIONTEST}
                    >
                        <FormControl display="flex" justifyContent="end">
                            <Switch
                                onChange={(event) =>
                                    props.onSelectAction({
                                        type: props.action.action,
                                        value: event.target.checked
                                    })
                                }
                                size="lg"
                                defaultChecked={props.actionDefaultValues.integrationtest}
                            />
                        </FormControl>
                    </ActionElement>
                ) : props.action.action === 'meetings' ? (
                    <ActionElement
                        title={
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                Meetings
                                <div className="tooltip-container" style={{ marginLeft: '8px' }}>
                                    <Tooltip
                                        label="Meetings are important for familiarity, set them regularly"
                                        isOpen={activeTooltip === 'meetings'}
                                    >
                                        <button onClick={() => handleButtonClick('meetings')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Set number of meetings"
                        icon={actionIcon.MEETINGS}
                    >
                        <Flex w="full">
                            <ActionSlider
                                onSlide={(event) =>
                                    props.onSelectAction({
                                        type: props.action.action,
                                        value: event
                                    })
                                }
                                lower_limit={props.action.lower_limit}
                                upper_limit={props.action.upper_limit}
                            />
                        </Flex>
                    </ActionElement>

                ) : props.action.action === 'training' ? (
                    <ActionElement
                        title={
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                Training
                                <div className="tooltip-container" style={{ marginLeft: '8px' }}>
                                    <Tooltip
                                        label="Training is important for motivation and familiarity"
                                        isOpen={activeTooltip === 'training'}
                                    >
                                        <button onClick={() => handleButtonClick('training')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Set training for employees"
                        icon={actionIcon.TRAINING}
                    >
                        <Flex w="full">
                            <ActionSlider
                                onSlide={(event) =>
                                    props.onSelectAction({
                                        type: props.action.action,
                                        value: event
                                    })
                                }
                                lower_limit={props.action.lower_limit}
                                upper_limit={props.action.upper_limit}
                            />
                        </Flex>
                    </ActionElement>

                ) : props.action.action === 'teamevent' ? (
                    <ActionElement
                        title={
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                Team Event
                                <div className="tooltip-container" style={{ marginLeft: '8px' }}>
                                    <Tooltip
                                        label="Team events reduce stress and rise motivation"
                                        isOpen={activeTooltip === 'teamevent'}
                                    >
                                        <button onClick={() => handleButtonClick('teamevent')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Schedule teamevent"
                        icon={actionIcon.TEAMEVENT}
                    >
                        <ActionToggle
                            onEventbutton={(event) =>
                                props.onSelectAction({
                                    type: props.action.action,
                                    value: event
                                })
                            }
                            textTrue="Scheduled"
                            textFalse="Not Scheduled"
                        />
                    </ActionElement>

                ) : props.action.action === 'salary' ? (
                    <ActionElement
                        title={
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                Salary
                                <div className="tooltip-container" style={{ marginLeft: '8px' }}>
                                    <Tooltip
                                        label="Different salaries for the employees can be set here"
                                        isOpen={activeTooltip === 'salary'}
                                    >
                                        <button onClick={() => handleButtonClick('salary')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Change Salary of employees"
                        icon={actionIcon.SALARY}
                    >
                        <ActionSelect
                            onActionSelect={(event) =>
                                props.onSelectAction({
                                    type: props.action.action,
                                    value: event
                                })
                            }
                            type="salary"
                            selection={['Below Average', 'Average', 'Above Average']}
                        />
                    </ActionElement>

                ) : props.action.action === 'overtime' ? (
                    <ActionElement
                        title={
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                Overtime
                                <div className="tooltip-container" style={{ marginLeft: '8px' }}>
                                    <Tooltip
                                        label="Overtime could be necessary for the project but will rise stress"
                                        isOpen={activeTooltip === 'overtime'}
                                    >
                                        <button onClick={() => handleButtonClick('overtime')}>
                                            <FaQuestionCircle size={12}/>
                                        </button>
                                    </Tooltip>
                                </div>
                            </div>
                        }
                        secondaryText="Change working hours"
                        icon={actionIcon.OVERTIME}
                    >
                        <ActionSelect
                            onActionSelect={(event) =>
                                props.onSelectAction({
                                    type: props.action.action,
                                    value: event
                                })
                            }
                            type="overtime"
                            selection={['Leave early', 'Normal hours', 'Encourage overtime', 'Enforce overtime']}
                        />
                    </ActionElement>

                ) : (
                    <></>
                )}
            </Grid>
        );
    } else {
        return <></>;
    }
}

export default Action