import React, { useEffect, useState } from "react";
import { Grid, Ref, Header, Container, Button } from "semantic-ui-react";
import config from "config.js";
import axios from "axios";
import { addDays, format, isSameDay } from "date-fns";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { BigNumber } from "bignumber.js";

function Plannif() {
  const api_url = config.api_url;

  const [plannifOrders, setPlannifOrders] = useState([]);
  const [planning, setPlanning] = useState([]);
  const [changedDays, setChangedDays] = useState([]);
  const [allOperations, setAllOperations] = useState([]);

  const moneyFormatter = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
  });

  function makeDay(date, orderLines) {
    return {
      date: date,
      orderLines: orderLines,
    };
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
    setChangedDays([planning[dayIndex]]);
  }

  async function fetchPlannifOrders() {
    return axios.get(`${api_url}/commandes?exact_status__in=12`);
  }

  async function fetchAllOperations() {
    return axios.get(`${api_url}/operations/`);
  }

  async function savePlannifLines(lines) {
    return axios.put(`${api_url}/lines/bulk_update/`, lines);
  }

  function getOrderById(id) {
    return plannifOrders.find((order) => order.exact_order_id === id);
  }

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
          allLines.filter((line) => !line.scheduled_at)
        ),
      ];
      for (let i = -3; i < 15; i++) {
        const date = addDays(new Date(), i);
        const lines = allLines.filter((line) => {
          return (
            line.scheduled_at && isSameDay(date, new Date(line.scheduled_at))
          );
        });
        initialPlanning.push(makeDay(date, lines));
      }
      setPlanning(initialPlanning);
    });
  }, []);

  useEffect(() => {
    savePlannifLines(
      changedDays
        .filter((day) => day.date)
        .map((day) => {
          return day.orderLines.map((line, index) => {
            line.scheduled_at = day.date;
            line.schedule_priority = index;
            return line;
          });
        })
        .flat()
    );
  }, [changedDays]);

  function onDragEnd(result) {
    const { source, destination } = result;

    // dropped outside the list or in the unscheduled orders
    if (!destination || destination.droppableId === 0) {
      return;
    }

    const sInd = +source.droppableId;
    const dInd = +destination.droppableId;

    if (sInd === dInd) {
      const day = reorderDay(planning[sInd], source.index, destination.index);
      const newPlanning = [...planning];
      newPlanning[sInd] = day;
      setPlanning(newPlanning);
      setChangedDays([day]);
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
      setChangedDays([newPlanning[sInd], newPlanning[dInd]]);
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
    <Container className="page-container">
      <DragDropContext onDragEnd={onDragEnd}>
        <Header as="h1"> Plannif </Header>
        {planning.map((day, dayIndex) => {
          return (
            <>
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
              <Droppable
                isDraggingOver={day.date === undefined}
                droppableId={`${dayIndex}`}
              >
                {(provided, snapshot) => (
                  <Ref innerRef={provided.innerRef}>
                    <Grid
                      divided="vertically"
                      columns={6}
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
                                  <Grid.Column width={2}>
                                    {order.exact_tier.exact_name}
                                  </Grid.Column>
                                  <Grid.Column width={2}>
                                    {order.exact_order_number}
                                  </Grid.Column>
                                  <Grid.Column width={2}>
                                    {order.exact_order_description}
                                  </Grid.Column>
                                  <Grid.Column width={2}>
                                    {line.item_code}
                                  </Grid.Column>
                                  <Grid.Column width={2}>
                                    {moneyFormatter.format(line.exact_amount)}
                                  </Grid.Column>
                                  <Grid.Column width={6}>
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
              <Header as="h3">{"Total: "}</Header>
            </>
          );
        })}
      </DragDropContext>
    </Container>
  );
}

export default Plannif;
