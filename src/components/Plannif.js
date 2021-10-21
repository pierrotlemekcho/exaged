import React, { useEffect, useState, useCallback } from "react";
import {
  Grid,
  Ref,
  Header,
  Form,
  Button,
  Icon,
  Dropdown,
} from "semantic-ui-react";
import config from "config.js";
import axiosInstance from "../axiosApi";
import AutoSaveText from "./AutoSaveText";
import {
  addDays,
  format,
  isSameDay,
  isBefore,
  startOfDay,
  isToday,
} from "date-fns";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { BigNumber } from "bignumber.js";
import { Link } from "react-router-dom";

function Plannif() {
  const DAYS_IN_THE_PAST = 7;
  const DAYS_IN_THE_FUTURE = 31;
  const api_url = config.api_url;

  const [plannifOrders, setPlannifOrders] = useState([]);
  const [planning, setPlanning] = useState([]);
  const [changedLines, setChangedLines] = useState([]);
  const [allOperations, setAllOperations] = useState([]);

  const partsStatusColorMap = {
    sur_place: "green",
    partiel: "yellow",
    non_dispo: "red",
  };

  const partsStatusOptions = [
    {
      key: 0,
      value: "sur_place",
      text: "Sur place",
      label: {
        circular: true,
        empty: true,
        color: "green",
      },
    },
    {
      key: 1,
      value: "partiel",
      text: "Partiel",
      label: {
        circular: true,
        empty: true,
        color: "yellow",
      },
    },
    {
      key: 2,
      value: "non_dispo",
      text: "Non dispo",
      label: {
        circular: true,
        empty: true,
        color: "red",
      },
    },
  ];

  const moneyFormatter = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  function makeDay(date, orderLines, sort = false) {
    if (sort) {
      orderLines.sort((a, b) => {
        return (a.schedule_priority || 0) - (b.schedule_priority || 0);
      });
    }
    orderLines = orderLines.map((line, index) => {
      line.scheduled_at = date ? startOfDay(date) : undefined;
      line.schedule_priority = index;
      return line;
    });
    return { date, orderLines };
  }

  function findHexColor(gamme) {
    const operation = allOperations.find(
      (operation) => operation.code === gamme
    );
    return operation ? operation.hex_color : "wrong";
  }

  function setCharAt(str, index, chr) {
    if (index > str.length - 1) return str;
    return str.substring(0, index) + chr + str.substring(index + 1);
  }

  function toggleGamme(dayIndex, lineIndex, position) {
    const line = planning[dayIndex].orderLines[lineIndex];
    let newGammeStatus = line.gamme_status;
    const gammeList = line.gamme_list;
    if (!line.gamme_status || line.gamme_status.length !== gammeList.length) {
      newGammeStatus = "".padStart(gammeList.length, "0");
    }
    if (newGammeStatus[position] === "1") {
      newGammeStatus = setCharAt(newGammeStatus, position, "0");
    } else {
      newGammeStatus = setCharAt(newGammeStatus, position, "1");
    }

    line.gamme_status = newGammeStatus;
    planning[dayIndex].orderLines[lineIndex] = line;
    setPlanning([...planning]);
    setChangedLines([line]);
  }

  function saveLineComments(dayIndex, lineIndex, value) {
    const line = planning[dayIndex].orderLines[lineIndex];
    line.comments = value;
    planning[dayIndex].orderLines[lineIndex] = line;
    setPlanning([...planning]);
    setChangedLines([line]);
  }

  function setPartsStatus(dayIndex, lineIndex, status) {
    debugger;
    const line = planning[dayIndex].orderLines[lineIndex];
    line.parts_status = status;
    planning[dayIndex].orderLines[lineIndex] = line;
    setPlanning([...planning]);
    setChangedLines([line]);
  }

  async function fetchPlannifOrders() {
    return axiosInstance.get(`${api_url}/commandes?exact_status__in=12`);
  }

  async function fetchAllOperations() {
    return axiosInstance.get(`${api_url}/operations/`);
  }

  async function savePlannifLines(lines) {
    return axiosInstance.put(`${api_url}/lines/bulk_update/`, lines);
  }

  function getOrderById(id) {
    return plannifOrders.find((order) => order.exact_order_id === id);
  }
  const todayRef = useCallback((node) => {
    if (node !== null) {
      const yOffset = -70;
      const y = node.getBoundingClientRect().top + window.pageYOffset + yOffset;
      window.scrollTo({ top: y });
    }
  }, []);

  useEffect(() => {
    fetchAllOperations().then((result) =>
      setAllOperations(result.data.results)
    );
    fetchPlannifOrders().then((result) => {
      setPlannifOrders(result.data.results);
      const allLines = result.data.results.map((order) => order.lines).flat();
      const initialPlanning = [
        makeDay(
          undefined,
          allLines.filter(
            (line) =>
              (line.gamme && !line.scheduled_at) ||
              isBefore(
                startOfDay(new Date(line.scheduled_at)),
                addDays(startOfDay(new Date()), -DAYS_IN_THE_PAST)
              )
          )
        ),
      ];
      for (let i = -DAYS_IN_THE_PAST; i < DAYS_IN_THE_FUTURE; i++) {
        const date = addDays(new Date(), i);
        const lines = allLines.filter((line) => {
          return (
            line.scheduled_at && isSameDay(date, new Date(line.scheduled_at))
          );
        });
        initialPlanning.push(makeDay(date, lines, true));
      }
      setPlanning(initialPlanning);
    });
  }, []);

  useEffect(() => {
    savePlannifLines(changedLines);
  }, [changedLines]);

  function onDragEnd(result) {
    const { source, destination } = result;

    // dropped outside the list or in the unscheduled orders
    if (!destination || destination.droppableId === "0") {
      return;
    }

    const sInd = +source.droppableId;
    const dInd = +destination.droppableId;

    if (sInd === dInd) {
      const day = reorderDay(planning[sInd], source.index, destination.index);
      const newPlanning = [...planning];
      newPlanning[sInd] = day;
      setPlanning(newPlanning);
      setChangedLines(day.orderLines);
    } else {
      const result = moveOrderLine(
        planning[sInd],
        planning[dInd],
        source,
        destination
      );
      const newPlanning = [...planning];
      newPlanning[sInd] = result[sInd];
      newPlanning[dInd] = result[dInd];
      setPlanning(newPlanning);
      let changedLines = [...newPlanning[dInd].orderLines];
      // Only save the source lines index if it's not the unscheduled orders
      if (sInd > 0) {
        changedLines.push(...newPlanning[sInd].orderLines);
      }
      setChangedLines(changedLines);
    }
  }

  function reorderDay(day, startIndex, endIndex) {
    const orderLines = [...day.orderLines];
    const [removed] = orderLines.splice(startIndex, 1);
    orderLines.splice(endIndex, 0, removed);
    return makeDay(day.date, orderLines);
  }

  function moveOrderLine(
    source,
    destination,
    droppableSource,
    droppableDestination
  ) {
    const sourceOrderLines = [...source.orderLines];
    const destinationOrderLines = [...destination.orderLines];

    const [removed] = sourceOrderLines.splice(droppableSource.index, 1);
    destinationOrderLines.splice(droppableDestination.index, 0, removed);

    const result = {};

    result[droppableSource.droppableId] = makeDay(
      source.date,
      sourceOrderLines
    );
    result[droppableDestination.droppableId] = makeDay(
      destination.date,
      destinationOrderLines
    );
    return result;
  }

  function getListStyle(isDraggingOver) {
    return {
      background: isDraggingOver ? "lightblue" : "lightgrey",
      padding: "8px",
    };
  }

  function getItemStyle(isDragging, draggableStyle) {
    return {
      // some basic styles to make the items look a bit nicer

      // change background colour if dragging
      background: isDragging ? "lightgreen" : "",

      // styles we need to apply on draggables
      ...draggableStyle,
    };
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Header as="h1"> Plannif </Header>
      {planning.map((day, dayIndex) => {
        return (
          <>
            <Ref innerRef={isToday(day.date) ? todayRef : undefined}>
              <Header as="h2">
                {" "}
                {day.date
                  ? format(day.date, "iiii d/MM/y")
                  : "Lignes non planifiees"}{" "}
                {" - "}
                {moneyFormatter.format(
                  day.orderLines.reduce((amount, line) => {
                    return amount.plus(BigNumber(line.exact_amount));
                  }, BigNumber(0))
                )}
              </Header>
            </Ref>
            <Droppable
              isDraggingOver={day.date === undefined}
              droppableId={`${dayIndex}`}
            >
              {(provided, snapshot) => (
                <Ref innerRef={provided.innerRef}>
                  <Grid
                    divided="vertically"
                    columns={7}
                    style={getListStyle(snapshot.isDraggingOver)}
                    {...provided.droppableProps}
                  >
                    {day.orderLines.map((line, lineIndex) => {
                      const order = getOrderById(line.exact_order_id);
                      return (
                        <Draggable
                          key={line.exact_id}
                          draggableId={line.exact_id}
                          index={lineIndex}
                        >
                          {(provided, snapshot) => (
                            <Ref innerRef={provided.innerRef}>
                              <Grid.Row
                                {...provided.draggableProps}
                                {...provided.dragHandleProps}
                                style={getItemStyle(
                                  snapshot.isDragging,
                                  provided.draggableProps.style
                                )}
                              >
                                <Grid.Column
                                  width={1}
                                  color={
                                    partsStatusColorMap[line.parts_status] ||
                                    "red"
                                  }
                                >
                                  <Dropdown
                                    value={line.parts_status || "non_dispo"}
                                    fluid
                                    labeled
                                    options={partsStatusOptions}
                                    onChange={(e, { value }) =>
                                      setPartsStatus(dayIndex, lineIndex, value)
                                    }
                                  />
                                </Grid.Column>
                                <Grid.Column width={2}>
                                  {order.exact_tier.exact_name}
                                </Grid.Column>
                                <Grid.Column width={1}>
                                  {order.exact_order_number}{" "}
                                  <Link
                                    to={`/documents?orderid=${order.id}`}
                                    target="_blank"
                                  >
                                    <Icon name="folder open" />
                                  </Link>
                                </Grid.Column>
                                <Grid.Column width={2}>
                                  {order.exact_order_description}
                                </Grid.Column>
                                <Grid.Column width={1}>
                                  {line.item_code}
                                </Grid.Column>
                                <Grid.Column width={2}>
                                  {moneyFormatter.format(line.exact_amount)}
                                </Grid.Column>
                                <Grid.Column width={2}>
                                  <Form>
                                    <AutoSaveText
                                      placeholder="Commentaires"
                                      value={line.comments}
                                      onSave={(value) => {
                                        return saveLineComments(
                                          dayIndex,
                                          lineIndex,
                                          value
                                        );
                                      }}
                                    />
                                  </Form>
                                </Grid.Column>
                                <Grid.Column width={4}>
                                  {line.gamme_list.map((gamme, position) => {
                                    return (
                                      <Button
                                        className={
                                          line.gamme_status[position] === "1"
                                            ? "green"
                                            : ""
                                        }
                                        style={
                                          line.gamme_status[position] !== "1"
                                            ? {
                                                backgroundColor: findHexColor(
                                                  gamme
                                                ),
                                              }
                                            : {}
                                        }
                                        onClick={() =>
                                          toggleGamme(
                                            dayIndex,
                                            lineIndex,
                                            position
                                          )
                                        }
                                      >
                                        {gamme}
                                      </Button>
                                    );
                                  })}
                                </Grid.Column>
                              </Grid.Row>
                            </Ref>
                          )}
                        </Draggable>
                      );
                    })}
                    {provided.placeholder}
                  </Grid>
                </Ref>
              )}
            </Droppable>
          </>
        );
      })}
    </DragDropContext>
  );
}

export default Plannif;
